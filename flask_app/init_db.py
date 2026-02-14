from __future__ import annotations

from app import app
from models import db


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("SQLite database initialized.")
