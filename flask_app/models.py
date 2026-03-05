from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Admins(db.Model):
    __tablename__ = "admins_table"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(512), nullable=False, default="")
    is_root = db.Column(db.Boolean, nullable=False, default=False)

    # Legacy column kept so SQLite doesn't complain about the old schema
    password = db.Column(db.String(255), nullable=True)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Updates(db.Model):
    __tablename__ = "updates_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), nullable=False, default="General")
    author_name = db.Column(db.String(120), nullable=False, default="Tweens Admin")
    excerpt = db.Column(db.Text, nullable=False, default="")
    caption = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="draft")
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Testimony(db.Model):
    __tablename__ = "testimony_table"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    caption = db.Column(db.Text, nullable=False)


class Newsletter(db.Model):
    __tablename__ = "newsletter_table"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)


class Contact(db.Model):
    __tablename__ = "contact_table"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)


class SiteContent(db.Model):
    __tablename__ = "site_content_table"
    __table_args__ = (
        UniqueConstraint("page", "section", "field", name="uq_site_content_key"),
    )

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(100), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Achievement(db.Model):
    __tablename__ = "achievements_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False, default="")
    text = db.Column(db.Text, nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class Program(db.Model):
    __tablename__ = "programs_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.String(100), nullable=False, default="academic")
    show_image = db.Column(db.String(255), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    media_images = db.relationship("ProgramMedia", backref="program", cascade="all, delete-orphan", order_by="ProgramMedia.sort_order")


class ProgramMedia(db.Model):
    __tablename__ = "program_media_table"

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("programs_table.id"), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class Activity(db.Model):
    __tablename__ = "activities_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    image = db.Column(db.String(255), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class HeroSlide(db.Model):
    __tablename__ = "hero_slides_table"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
