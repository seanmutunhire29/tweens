from __future__ import annotations

from app import app
from db_migrations import run_migrations


if __name__ == "__main__":
    with app.app_context():
        run_migrations()
    print("Migration 0001 applied: site_content_table")
