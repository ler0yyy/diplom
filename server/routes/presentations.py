from typing import Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from ..app import db
from ..models import Presentation, Slide, SlideOption


bp = Blueprint("presentations", __name__, url_prefix="/api")


def _require_teacher():
    claims = get_jwt()
    if claims.get("role") != "teacher":
        return jsonify({"error": "forbidden"}), 403
    return None


def _teacher_id() -> int:
    return int(get_jwt_identity())


def _get_owned_presentation(presentation_id: int) -> Optional[Presentation]:
    p = Presentation.query.get(presentation_id)
    if not p or p.teacher_id != _teacher_id():
        return None
    return p


def _get_owned_slide(slide_id: int) -> Optional[Slide]:
    slide = Slide.query.get(slide_id)
    if not slide:
        return None
    p = Presentation.query.get(slide.presentation_id)
    if not p or p.teacher_id != _teacher_id():
        return None
    return slide


@bp.get("/presentations")
@jwt_required()
def list_presentations():
    forbid = _require_teacher()
    if forbid:
        return forbid

    teacher_id = _teacher_id()
    items = (
        Presentation.query.filter_by(teacher_id=teacher_id)
        .order_by(Presentation.created_at.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in items
        ]
    )


@bp.post("/presentations")
@jwt_required()
def create_presentation():
    forbid = _require_teacher()
    if forbid:
        return forbid

    data = request.get_json(force=True) or {}
    title = (data.get("title") or "").strip()
    description = data.get("description")
    if not title:
        return jsonify({"error": "invalid_payload"}), 400

    teacher_id = _teacher_id()
    p = Presentation(teacher_id=teacher_id, title=title, description=description)
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id, "title": p.title, "description": p.description}), 201


@bp.put("/presentations/<int:presentation_id>")
@jwt_required()
def update_presentation(presentation_id: int):
    forbid = _require_teacher()
    if forbid:
        return forbid

    p = _get_owned_presentation(presentation_id)
    if not p:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(force=True) or {}
    title = (data.get("title") or "").strip()
    description = data.get("description")

    if title:
        p.title = title
    if description is not None:
        p.description = description

    db.session.commit()
    return jsonify({"ok": True})


@bp.delete("/presentations/<int:presentation_id>")
@jwt_required()
def delete_presentation(presentation_id: int):
    forbid = _require_teacher()
    if forbid:
        return forbid

    p = _get_owned_presentation(presentation_id)
    if not p:
        return jsonify({"error": "not_found"}), 404

    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/presentations/<int:presentation_id>/slides")
@jwt_required(optional=True)
def list_slides(presentation_id: int):
    slides = (
        Slide.query.filter_by(presentation_id=presentation_id)
        .order_by(Slide.order_index.asc(), Slide.id.asc())
        .all()
    )
    result = []
    for s in slides:
        options = SlideOption.query.filter_by(slide_id=s.id).order_by(SlideOption.id.asc()).all()
        result.append(
            {
                "id": s.id,
                "presentation_id": s.presentation_id,
                "order_index": s.order_index,
                "question": s.question,
                "test_type": s.test_type,
                "options": [{"id": o.id, "label": o.label, "text": o.text} for o in options],
            }
        )
    return jsonify(result)


@bp.post("/presentations/<int:presentation_id>/slides")
@jwt_required()
def add_slide(presentation_id: int):
    forbid = _require_teacher()
    if forbid:
        return forbid

    p = _get_owned_presentation(presentation_id)
    if not p:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(force=True) or {}
    question = (data.get("question") or "").strip()
    test_type = data.get("test_type")
    options = data.get("options") or []

    existing_count = Slide.query.filter_by(presentation_id=presentation_id).count()
    order_index = int(data.get("order_index") if data.get("order_index") is not None else existing_count)

    if not question or test_type not in ("choice", "tags"):
        return jsonify({"error": "invalid_payload"}), 400

    slide = Slide(
        presentation_id=presentation_id,
        question=question,
        test_type=test_type,
        order_index=order_index,
    )
    db.session.add(slide)
    db.session.flush()

    if test_type == "choice":
        if not isinstance(options, list) or len(options) < 2:
            return jsonify({"error": "choice_requires_options"}), 400
        for idx, opt in enumerate(options):
            text = (opt.get("text") or "").strip()
            if not text:
                return jsonify({"error": "invalid_option"}), 400
            label = opt.get("label") or chr(65 + idx)
            db.session.add(SlideOption(slide_id=slide.id, label=label, text=text))

    db.session.commit()
    return jsonify({"id": slide.id}), 201


@bp.put("/slides/<int:slide_id>")
@jwt_required()
def update_slide(slide_id: int):
    forbid = _require_teacher()
    if forbid:
        return forbid

    slide = _get_owned_slide(slide_id)
    if not slide:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(force=True) or {}

    question = (data.get("question") or "").strip()
    test_type = data.get("test_type")
    order_index = data.get("order_index")
    options = data.get("options")

    if question:
        slide.question = question
    if test_type in ("choice", "tags"):
        slide.test_type = test_type
    if order_index is not None:
        slide.order_index = int(order_index)

    if options is not None:
        SlideOption.query.filter_by(slide_id=slide.id).delete()
        if slide.test_type == "choice":
            if not isinstance(options, list) or len(options) < 2:
                return jsonify({"error": "choice_requires_options"}), 400
            for idx, opt in enumerate(options):
                text = (opt.get("text") or "").strip()
                if not text:
                    return jsonify({"error": "invalid_option"}), 400
                label = opt.get("label") or chr(65 + idx)
                db.session.add(SlideOption(slide_id=slide.id, label=label, text=text))

    db.session.commit()
    return jsonify({"ok": True})


@bp.delete("/slides/<int:slide_id>")
@jwt_required()
def delete_slide(slide_id: int):
    forbid = _require_teacher()
    if forbid:
        return forbid

    slide = _get_owned_slide(slide_id)
    if not slide:
        return jsonify({"error": "not_found"}), 404

    SlideOption.query.filter_by(slide_id=slide_id).delete()
    db.session.delete(slide)
    db.session.commit()
    return jsonify({"ok": True})

