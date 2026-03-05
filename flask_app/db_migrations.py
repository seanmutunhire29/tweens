from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, UniqueConstraint, Boolean
from sqlalchemy import inspect, text

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

    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())
    if "updates_table" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("updates_table")}
    statements = []

    if "category" not in existing_columns:
        statements.append("ALTER TABLE updates_table ADD COLUMN category VARCHAR(120) DEFAULT 'General'")
    if "author_name" not in existing_columns:
        statements.append("ALTER TABLE updates_table ADD COLUMN author_name VARCHAR(120) DEFAULT 'Tweens Admin'")
    if "excerpt" not in existing_columns:
        statements.append("ALTER TABLE updates_table ADD COLUMN excerpt TEXT DEFAULT ''")
    if "status" not in existing_columns:
        statements.append("ALTER TABLE updates_table ADD COLUMN status VARCHAR(20) DEFAULT 'draft'")
    if "published_at" not in existing_columns:
        statements.append("ALTER TABLE updates_table ADD COLUMN published_at DATETIME")

    if statements:
        with db.engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))

    with db.engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE updates_table
                SET
                    category = COALESCE(NULLIF(category, ''), 'General'),
                    author_name = COALESCE(NULLIF(author_name, ''), 'Tweens Admin'),
                    excerpt = COALESCE(NULLIF(excerpt, ''), SUBSTR(detail, 1, 220)),
                    status = COALESCE(NULLIF(status, ''), 'published'),
                    published_at = COALESCE(published_at, created_at)
                """
            )
        )

    # ── Migrate admins_table: add password_hash, is_root columns ──
    if "admins_table" in table_names:
        admin_cols = {col["name"] for col in inspector.get_columns("admins_table")}
        admin_stmts = []
        if "password_hash" not in admin_cols:
            admin_stmts.append("ALTER TABLE admins_table ADD COLUMN password_hash VARCHAR(512) DEFAULT ''")
        if "is_root" not in admin_cols:
            admin_stmts.append("ALTER TABLE admins_table ADD COLUMN is_root BOOLEAN DEFAULT 0")
        if admin_stmts:
            with db.engine.begin() as connection:
                for stmt in admin_stmts:
                    connection.execute(text(stmt))
