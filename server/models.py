from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from .app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('student', 'teacher')", name="users_role_check"),
    )


class Presentation(db.Model):
    __tablename__ = "presentations"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)


class Slide(db.Model):
    __tablename__ = "slides"

    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    question = db.Column(db.Text, nullable=False)
    test_type = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default="false")

    __table_args__ = (
        CheckConstraint("test_type IN ('choice', 'tags')", name="slides_test_type_check"),
    )


class SlideOption(db.Model):
    __tablename__ = "slide_options"

    id = db.Column(db.Integer, primary_key=True)
    slide_id = db.Column(db.Integer, db.ForeignKey("slides.id", ondelete="CASCADE"), nullable=False, index=True)
    label = db.Column(db.String(1), nullable=True)
    text = db.Column(db.Text, nullable=False)


class PollSession(db.Model):
    __tablename__ = "poll_sessions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slide_id = db.Column(db.Integer, db.ForeignKey("slides.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = db.Column(db.DateTime(timezone=True), nullable=True)


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey("poll_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    option_id = db.Column(db.Integer, db.ForeignKey("slide_options.id"), nullable=True, index=True)
    tags = db.Column(ARRAY(db.Text), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="responses_session_user_unique"),
    )

