from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Admins(db.Model):
    __tablename__ = "admins_table"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Updates(db.Model):
    __tablename__ = "updates_table"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=False)
    detail = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)


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
