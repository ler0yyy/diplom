from __future__ import annotations

import uuid
from collections import Counter

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func

from ..app import db
from ..models import PollSession, Response, Slide, SlideOption


bp = Blueprint("poll", __name__, url_prefix="/api")


@bp.post("/sessions")
@jwt_required()
def create_session():
    """
    POST /api/sessions
    Payload: { "slide_id": number, "reuse": boolean (optional) }
    Returns: { "session_id": "uuid" }
    Only authenticated users (teachers) can create sessions.
    If reuse=true, returns existing active session for the slide if available.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    # Only teachers can create sessions
    if claims.get("role") != "teacher":
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(force=True) or {}
    slide_id = data.get("slide_id")
    reuse = data.get("reuse", True)  # Default to reuse existing session

    if not slide_id:
        return jsonify({"error": "invalid_payload"}), 400

    # Verify the slide belongs to this teacher
    slide = Slide.query.get(slide_id)
    if not slide:
        return jsonify({"error": "slide_not_found"}), 404

    from ..models import Presentation
    presentation = Presentation.query.get(slide.presentation_id)
    if not presentation or presentation.teacher_id != user_id:
        return jsonify({"error": "forbidden"}), 403

    # If reuse is True, look for existing active session (no closed_at)
    if reuse:
        from sqlalchemy import desc
        print(f"[SESSION] Looking for active session for slide {slide.id}")
        existing = (
            PollSession.query
            .filter(PollSession.slide_id == slide.id)
            .filter(PollSession.closed_at.is_(None))
            .order_by(desc(PollSession.started_at))
            .first()
        )
        print(f"[SESSION] Found: {existing}")
        if existing:
            print(f"[SESSION] Reusing {existing.id}")
            return jsonify({"session_id": str(existing.id), "reused": True}), 200
        print(f"[SESSION] Creating new session")

    # Create new session
    session = PollSession(slide_id=slide.id)
    db.session.add(session)
    db.session.commit()
    return jsonify({"session_id": str(session.id), "reused": False}), 201


@bp.post("/responses")
@jwt_required()
def submit_response():
    """
    POST /api/responses
    Payload: { session_id, option_id? , tags? }
    """
    user_id = int(get_jwt_identity())

    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")
    option_id = data.get("option_id")
    tags = data.get("tags")

    try:
        session_uuid = uuid.UUID(str(session_id))
    except Exception:
        return jsonify({"error": "invalid_session_id"}), 400

    session = PollSession.query.get(session_uuid)
    if not session:
        return jsonify({"error": "session_not_found"}), 404

    slide = Slide.query.get(session.slide_id)
    if not slide:
        return jsonify({"error": "slide_not_found"}), 404

    # upsert semantics: overwrite previous answer
    existing = Response.query.filter_by(session_id=session.id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.flush()

    if slide.test_type == "choice":
        if not option_id:
            return jsonify({"error": "option_required"}), 400
        opt = SlideOption.query.filter_by(id=option_id, slide_id=slide.id).first()
        if not opt:
            return jsonify({"error": "option_not_found"}), 404
        resp = Response(session_id=session.id, user_id=user_id, option_id=opt.id, tags=None)
    else:
        if tags is None:
            return jsonify({"error": "tags_required"}), 400
        if isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        elif isinstance(tags, list):
            tags_list = [str(t).strip() for t in tags if str(t).strip()]
        else:
            return jsonify({"error": "invalid_tags"}), 400
        resp = Response(session_id=session.id, user_id=user_id, option_id=None, tags=tags_list)

    db.session.add(resp)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/sessions/<session_id>/stats")
def session_stats(session_id: str):
    try:
        session_uuid = uuid.UUID(session_id)
    except Exception:
        return jsonify({"error": "invalid_session_id"}), 400

    session = PollSession.query.get(session_uuid)
    if not session:
        return jsonify({"error": "session_not_found"}), 404

    slide = Slide.query.get(session.slide_id)
    if not slide:
        return jsonify({"error": "slide_not_found"}), 404

    if slide.test_type == "choice":
        options = SlideOption.query.filter_by(slide_id=slide.id).order_by(SlideOption.id.asc()).all()
        total = db.session.query(func.count(Response.id)).filter(Response.session_id == session.id).scalar() or 0
        votes_by_option = dict(
            db.session.query(Response.option_id, func.count(Response.id))
            .filter(Response.session_id == session.id)
            .group_by(Response.option_id)
            .all()
        )
        items = []
        for o in options:
            votes = int(votes_by_option.get(o.id, 0))
            percent = int(round((votes / total) * 100)) if total else 0
            label = f"{o.label}: {o.text}" if o.label else o.text
            items.append({"label": label, "votes": votes, "percent": percent})
        return jsonify({"question": slide.question, "total": int(total), "items": items, "tags": []})

    # tags
    total = db.session.query(func.count(Response.id)).filter(Response.session_id == session.id).scalar() or 0
    rows = db.session.query(Response.tags).filter(Response.session_id == session.id).all()
    words: list[str] = []
    for (arr,) in rows:
        if not arr:
            continue
        for w in arr:
            s = str(w).strip()
            if s:
                words.append(s)
    counts = Counter(words)
    tags_out = [{"word": w, "count": int(c)} for w, c in counts.most_common(30)]
    return jsonify({"question": slide.question, "total": int(total), "items": [], "tags": tags_out})


@bp.get("/sessions/<session_id>/poll")
def session_poll(session_id: str):
    """
    Для сайта: получить вопрос и опции по session_id.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except Exception:
        return jsonify({"error": "invalid_session_id"}), 400

    session = PollSession.query.get(session_uuid)
    if not session:
        return jsonify({"error": "session_not_found"}), 404

    slide = Slide.query.get(session.slide_id)
    if not slide:
        return jsonify({"error": "slide_not_found"}), 404

    options = []
    if slide.test_type == "choice":
        rows = SlideOption.query.filter_by(slide_id=slide.id).order_by(SlideOption.id.asc()).all()
        options = [{"id": o.id, "label": o.label, "text": o.text} for o in rows]

    return jsonify(
        {
            "session_id": str(session.id),
            "slide_id": slide.id,
            "question": slide.question,
            "test_type": slide.test_type,
            "options": options,
        }
    )


@bp.get("/ppt/slide/<int:slide_id>/stats")
def ppt_slide_stats(slide_id: int):
    # Для VBA: берём последнюю (по started_at) сессию для slide_id
    session = (
        PollSession.query.filter_by(slide_id=slide_id)
        .order_by(PollSession.started_at.desc())
        .first()
    )
    if not session:
        return jsonify({"error": "session_not_found"}), 404
    return session_stats(str(session.id))

