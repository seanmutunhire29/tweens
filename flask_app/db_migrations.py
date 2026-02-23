from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, UniqueConstraint

from models import db


def run_migrations() -> None:
    metadata = MetaData()

    site_content_table = Table(
        "site_content_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("page", String(100), nullable=False),
        Column("section", String(100), nullable=False),
        Column("field", String(100), nullable=False),
        Column("value", Text, nullable=False),
        Column("updated_at", DateTime, nullable=False, default=datetime.utcnow),
        UniqueConstraint("page", "section", "field", name="uq_site_content_key"),
    )

    site_content_table.create(bind=db.engine, checkfirst=True)
