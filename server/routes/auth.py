from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from ..app import bcrypt, db
from ..models import User


bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    role = data.get("role") or ""

    if not email or not password or not name or role not in ("student", "teacher"):
        return jsonify({"error": "invalid_payload"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_taken"}), 409

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=pw_hash, name=name, role=role)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(
        {
            "token": token,
            "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
        }
    ), 201


@bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "invalid_payload"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid_credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(
        {
            "token": token,
            "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
        }
    )

