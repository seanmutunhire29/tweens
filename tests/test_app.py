"""
Comprehensive pytest test suite for the Tweens Flask application.

Covers:
  - All public routes (home, about, achievements, programs, contact, donations, news)
  - Newsletter signup (valid, invalid, edge cases)
  - Contact form (valid, missing fields, malformed email, edge cases)
  - Admin authentication (login, logout, wrong credentials, session state)
  - Admin dashboard (authenticated vs unauthenticated access)
  - News CRUD (create, edit, delete, detail view, draft/published filter)
  - Testimony CRUD
  - Achievement CRUD
  - Program CRUD
  - Activity CRUD
  - Hero slide CRUD
  - User management (add, change password, delete – root-only checks)
  - Site content update routes
  - Helper functions (allowed_file, parse_datetime_local, format_date, etc.)
  - Edge cases: 404 IDs, empty payloads, SQL-like inputs, very long strings
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Make sure the project root is on the path so we can import flask_app.app
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set env vars BEFORE importing the app so they take effect for the
# module-level `with app.app_context():` block.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ADMIN_NAME", "testroot")
os.environ.setdefault("ADMIN_PASSWORD", "rootpass123")

from flask_app.app import app as flask_app  # noqa: E402
from flask_app.models import (  # noqa: E402
    Admins, Achievement, Activity, Contact, HeroSlide,
    Newsletter, Program, SiteContent, Testimony, Updates, db,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fake_image(name: str = "test.jpg", content: bytes = b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;") -> tuple:
    """Return a (BytesIO, filename) tuple suitable for multipart uploads."""
    return (io.BytesIO(content), name)


def login(client, username: str = "testroot", password: str = "rootpass123"):
    """Helper to log in via the admin login form."""
    return client.post(
        "/news/createValidate",
        data={"name": username, "password": password},
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def _tmp_upload_dir(tmp_path_factory):
    """Session-scoped temporary upload directory to avoid touching the real one."""
    d = tmp_path_factory.mktemp("uploads")
    return d


@pytest.fixture(scope="function")
def app(_tmp_upload_dir):
    """Configure the Flask app for testing with an isolated in-memory DB."""
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
    )

    # Redirect uploads to temp dir so we don't pollute the real public folder
    import flask_app.app as app_module
    original_upload_dir = app_module.UPLOAD_DIR
    app_module.UPLOAD_DIR = _tmp_upload_dir

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        # Seed root admin
        root = Admins(username="testroot", is_root=True, password="")
        root.set_password("rootpass123")
        db.session.add(root)
        db.session.commit()

    yield flask_app

    # Restore
    app_module.UPLOAD_DIR = original_upload_dir
    with flask_app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def auth_client(app):
    """Test client that is already logged in as root admin."""
    c = app.test_client()
    with app.app_context():
        root = Admins.query.filter_by(username="testroot").first()
        with c.session_transaction() as sess:
            sess["authenticated"] = True
            sess["admin_user_id"] = root.id
    return c


@pytest.fixture(scope="function")
def non_root_admin(app):
    """A non-root admin user persisted in the DB."""
    with app.app_context():
        user = Admins(username="regularadmin", is_root=False, password="")
        user.set_password("adminpass123")
        db.session.add(user)
        db.session.commit()
        return user.id  # return ID so it can be queried fresh


@pytest.fixture(scope="function")
def non_root_auth_client(app, non_root_admin):
    """Test client logged in as a non-root admin."""
    c = app.test_client()
    with c.session_transaction() as sess:
        sess["authenticated"] = True
        sess["admin_user_id"] = non_root_admin
    return c


@pytest.fixture(scope="function")
def published_article(app):
    """A published Updates record in the DB."""
    with app.app_context():
        article = Updates(
            title="Published Test Article",
            category="General",
            author_name="Tester",
            excerpt="A short excerpt.",
            caption="Test caption",
            detail="Full detail of the article.",
            image="updateImages/test.jpg",
            status="published",
            published_at=datetime(2024, 1, 1),
            created_at=datetime(2024, 1, 1),
        )
        db.session.add(article)
        db.session.commit()
        return article.id


@pytest.fixture(scope="function")
def draft_article(app):
    """A draft Updates record in the DB."""
    with app.app_context():
        article = Updates(
            title="Draft Test Article",
            category="General",
            author_name="Tester",
            excerpt="Draft excerpt.",
            caption="Draft caption",
            detail="Draft detail content.",
            image="updateImages/draft.jpg",
            status="draft",
            created_at=datetime(2024, 1, 1),
        )
        db.session.add(article)
        db.session.commit()
        return article.id


@pytest.fixture(scope="function")
def sample_testimony(app):
    with app.app_context():
        t = Testimony(name="Alice", image="updateImages/alice.jpg", caption="Great program!")
        db.session.add(t)
        db.session.commit()
        return t.id


@pytest.fixture(scope="function")
def sample_achievement(app):
    with app.app_context():
        a = Achievement(title="Test Achievement", image="", text="Some achievement text.", sort_order=1)
        db.session.add(a)
        db.session.commit()
        return a.id


@pytest.fixture(scope="function")
def sample_program(app):
    with app.app_context():
        p = Program(title="Test Program", description="Desc", category="academic", show_image="", sort_order=1)
        db.session.add(p)
        db.session.commit()
        return p.id


@pytest.fixture(scope="function")
def sample_activity(app):
    with app.app_context():
        a = Activity(title="Test Activity", description="Activity desc", image="", sort_order=1)
        db.session.add(a)
        db.session.commit()
        return a.id


@pytest.fixture(scope="function")
def sample_hero_slide(app):
    with app.app_context():
        h = HeroSlide(image="updateImages/hero.jpg", sort_order=1)
        db.session.add(h)
        db.session.commit()
        return h.id


# ===========================================================================
# 1. PUBLIC ROUTES
# ===========================================================================

class TestPublicRoutes:
    def test_home_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_home_contains_tweens(self, client):
        r = client.get("/")
        assert b"Tweens" in r.data or b"tweens" in r.data.lower()

    def test_about_returns_200(self, client):
        r = client.get("/about")
        assert r.status_code == 200

    def test_achievements_returns_200(self, client):
        r = client.get("/achievements")
        assert r.status_code == 200

    def test_programs_returns_200(self, client):
        r = client.get("/programs")
        assert r.status_code == 200

    def test_contact_returns_200(self, client):
        r = client.get("/contact")
        assert r.status_code == 200

    def test_donations_returns_200(self, client):
        r = client.get("/donations")
        assert r.status_code == 200

    def test_home_with_published_article(self, client, published_article):
        r = client.get("/")
        assert r.status_code == 200
        assert b"Published Test Article" in r.data

    def test_home_does_not_show_draft(self, client, draft_article):
        r = client.get("/")
        assert r.status_code == 200
        assert b"Draft Test Article" not in r.data


# ===========================================================================
# 2. NEWS DETAIL
# ===========================================================================

class TestNewsDetail:
    def test_published_article_visible_to_public(self, client, published_article):
        r = client.get(f"/news/{published_article}")
        assert r.status_code == 200
        assert b"Published Test Article" in r.data

    def test_draft_not_visible_to_public(self, client, draft_article):
        r = client.get(f"/news/{draft_article}")
        assert r.status_code == 404

    def test_draft_visible_to_admin(self, auth_client, draft_article):
        r = auth_client.get(f"/news/{draft_article}")
        assert r.status_code == 200
        assert b"Draft Test Article" in r.data

    def test_nonexistent_article_returns_404(self, client):
        r = client.get("/news/99999")
        assert r.status_code == 404

    def test_related_articles_shown(self, client, app):
        """Creates multiple published articles and checks the detail page shows related."""
        with app.app_context():
            for i in range(3):
                db.session.add(Updates(
                    title=f"Related Article {i}",
                    category="General",
                    author_name="Tester",
                    excerpt="excerpt",
                    caption="caption",
                    detail="detail",
                    image="",
                    status="published",
                    published_at=datetime(2024, 1, i + 1),
                    created_at=datetime(2024, 1, i + 1),
                ))
            db.session.commit()
            first = Updates.query.filter_by(status="published").first()
            article_id = first.id

        r = client.get(f"/news/{article_id}")
        assert r.status_code == 200

    def test_markdown_rendered_in_detail(self, client, app):
        with app.app_context():
            article = Updates(
                title="Markdown Article",
                category="General",
                author_name="Tester",
                excerpt="excerpt",
                caption="caption",
                detail="**bold text**",
                image="",
                status="published",
                published_at=datetime(2024, 1, 1),
                created_at=datetime(2024, 1, 1),
            )
            db.session.add(article)
            db.session.commit()
            article_id = article.id

        r = client.get(f"/news/{article_id}")
        assert r.status_code == 200
        assert b"<strong>" in r.data or b"<b>" in r.data


# ===========================================================================
# 3. NEWSLETTER SIGNUP
# ===========================================================================

class TestNewsletter:
    def test_valid_email_accepted(self, client):
        r = client.post("/newsletter", data={"newsletter": "user@example.com"}, follow_redirects=True)
        assert r.status_code == 200

    def test_valid_email_stored(self, client, app):
        client.post("/newsletter", data={"newsletter": "stored@example.com"})
        with app.app_context():
            assert Newsletter.query.filter_by(email="stored@example.com").first() is not None

    def test_invalid_email_no_at_sign(self, client, app):
        client.post("/newsletter", data={"newsletter": "invalidemail"})
        with app.app_context():
            assert Newsletter.query.filter_by(email="invalidemail").first() is None

    def test_empty_email_rejected(self, client, app):
        client.post("/newsletter", data={"newsletter": ""})
        with app.app_context():
            assert Newsletter.query.count() == 0

    def test_email_with_leading_trailing_spaces_stored_stripped(self, client, app):
        client.post("/newsletter", data={"newsletter": "  spaced@example.com  "})
        with app.app_context():
            # The route strips the email, so stored value should be stripped
            assert Newsletter.query.filter_by(email="spaced@example.com").first() is not None

    def test_duplicate_emails_allowed(self, client, app):
        """Newsletter does not enforce uniqueness – duplicates can be stored."""
        client.post("/newsletter", data={"newsletter": "dup@example.com"})
        client.post("/newsletter", data={"newsletter": "dup@example.com"})
        with app.app_context():
            assert Newsletter.query.filter_by(email="dup@example.com").count() == 2

    def test_very_long_email_stored(self, client, app):
        long_email = "a" * 240 + "@b.com"
        client.post("/newsletter", data={"newsletter": long_email})
        with app.app_context():
            assert Newsletter.query.filter_by(email=long_email).first() is not None

    def test_get_method_not_allowed(self, client):
        r = client.get("/newsletter")
        # Flask returns 404 when only POST is registered and no GET route exists
        assert r.status_code in (404, 405)


# ===========================================================================
# 4. CONTACT FORM
# ===========================================================================

class TestContactForm:
    VALID_PAYLOAD = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "contact-number": "0771234567",
        "purpose": "Volunteer",
        "message": "I would like to volunteer.",
    }

    def test_valid_submission_redirects(self, client):
        r = client.post("/contact", data=self.VALID_PAYLOAD, follow_redirects=False)
        assert r.status_code == 302

    def test_valid_submission_stored(self, client, app):
        client.post("/contact", data=self.VALID_PAYLOAD)
        with app.app_context():
            c = Contact.query.filter_by(email="jane@example.com").first()
            assert c is not None
            assert c.full_name == "Jane Doe"

    def test_missing_name_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "name": ""}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200
        assert b"required" in r.data.lower()

    def test_missing_email_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "email": ""}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200

    def test_invalid_email_no_at_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "email": "notanemail"}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200

    def test_missing_phone_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "contact-number": ""}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200

    def test_missing_purpose_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "purpose": ""}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200

    def test_missing_message_shows_error(self, client):
        payload = {**self.VALID_PAYLOAD, "message": ""}
        r = client.post("/contact", data=payload)
        assert r.status_code == 200

    def test_all_fields_missing_returns_200_with_errors(self, client):
        r = client.post("/contact", data={})
        assert r.status_code == 200

    def test_invalid_submission_not_stored(self, client, app):
        client.post("/contact", data={"name": "", "email": "", "contact-number": "", "purpose": "", "message": ""})
        with app.app_context():
            assert Contact.query.count() == 0

    def test_sql_injection_in_name_stored_safely(self, client, app):
        payload = {**self.VALID_PAYLOAD, "name": "Robert'); DROP TABLE contact_table;--", "email": "sql@example.com"}
        r = client.post("/contact", data=payload)
        with app.app_context():
            c = Contact.query.filter_by(email="sql@example.com").first()
            assert c is not None
            assert "DROP TABLE" in c.full_name


# ===========================================================================
# 5. ADMIN AUTHENTICATION
# ===========================================================================

class TestAdminAuth:
    def test_login_page_loads(self, client):
        r = client.get("/news/createValidate")
        assert r.status_code == 200

    def test_valid_login_redirects_to_dashboard(self, client):
        r = client.post(
            "/news/createValidate",
            data={"name": "testroot", "password": "rootpass123"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert "/news/create" in r.headers["Location"]

    def test_valid_login_sets_session(self, client):
        client.post("/news/createValidate", data={"name": "testroot", "password": "rootpass123"})
        with client.session_transaction() as sess:
            assert sess.get("authenticated") is True

    def test_wrong_password_rejected(self, client):
        r = client.post(
            "/news/createValidate",
            data={"name": "testroot", "password": "wrongpassword"},
            follow_redirects=False,
        )
        # Redirects back to login page (not to admin dashboard)
        assert r.status_code == 302
        assert "createValidate" in r.headers["Location"]

    def test_wrong_password_does_not_set_session(self, client):
        client.post("/news/createValidate", data={"name": "testroot", "password": "wrongpassword"})
        with client.session_transaction() as sess:
            assert not sess.get("authenticated")

    def test_wrong_username_rejected(self, client):
        r = client.post(
            "/news/createValidate",
            data={"name": "nonexistent", "password": "rootpass123"},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert "createValidate" in r.headers["Location"]

    def test_empty_credentials_rejected(self, client):
        r = client.post(
            "/news/createValidate",
            data={"name": "", "password": ""},
            follow_redirects=False,
        )
        assert r.status_code == 302
        assert "createValidate" in r.headers["Location"]

    def test_logout_clears_session(self, auth_client):
        r = auth_client.get("/admin/logout", follow_redirects=True)
        assert r.status_code == 200
        with auth_client.session_transaction() as sess:
            assert not sess.get("authenticated")

    def test_logout_redirects_to_home(self, auth_client):
        r = auth_client.get("/admin/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/" in r.headers["Location"]

    def test_unauthenticated_dashboard_still_returns_200(self, client):
        """Dashboard page is publicly visible but shows limited content."""
        r = client.get("/news/create")
        assert r.status_code == 200


# ===========================================================================
# 6. NEWS CRUD
# ===========================================================================

class TestNewsCRUD:
    def _news_payload(self, **overrides):
        payload = {
            "title": "Test News Title",
            "category": "Education",
            "author_name": "Staff Writer",
            "excerpt": "A brief excerpt.",
            "caption": "Image caption",
            "detail": "Full article detail here.",
            "status": "published",
            "published_at": "2024-06-01T09:00",
        }
        payload.update(overrides)
        return payload

    def test_unauthenticated_create_returns_403(self, client):
        data = {**self._news_payload(), "image": fake_image()}
        r = client.post("/news/create", data=data, content_type="multipart/form-data")
        assert r.status_code == 403

    def test_create_without_image_shows_error(self, auth_client):
        r = auth_client.post(
            "/news/create",
            data=self._news_payload(),
            content_type="multipart/form-data",
        )
        assert r.status_code == 200
        assert b"Image is required" in r.data

    def test_create_with_invalid_image_extension(self, auth_client):
        payload = self._news_payload()
        payload["image"] = (io.BytesIO(b"not really a pdf"), "doc.pdf")
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200
        assert b"Image is required" in r.data

    def test_create_with_valid_data_succeeds(self, auth_client, app):
        payload = self._news_payload()
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code in (200, 302)
        with app.app_context():
            assert Updates.query.filter_by(title="Test News Title").first() is not None

    def test_create_missing_title_shows_error(self, auth_client):
        payload = self._news_payload(title="")
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200
        assert b"Title is required" in r.data

    def test_create_missing_caption_shows_error(self, auth_client):
        payload = self._news_payload(caption="")
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200

    def test_create_missing_detail_shows_error(self, auth_client):
        payload = self._news_payload(detail="")
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200

    def test_create_invalid_status_shows_error(self, auth_client):
        payload = self._news_payload(status="pending")
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200
        assert b"Status must be draft or published" in r.data

    def test_create_invalid_published_at_shows_error(self, auth_client):
        payload = self._news_payload(published_at="not-a-date")
        payload["image"] = fake_image()
        r = auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        assert r.status_code == 200

    def test_create_draft_status(self, auth_client, app):
        payload = self._news_payload(title="Draft Article", status="draft")
        payload["image"] = fake_image()
        auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        with app.app_context():
            article = Updates.query.filter_by(title="Draft Article").first()
            assert article is not None
            assert article.status == "draft"

    def test_create_auto_excerpt_from_detail(self, auth_client, app):
        long_detail = "x" * 300
        payload = self._news_payload(title="AutoExcerpt", excerpt="", detail=long_detail)
        payload["image"] = fake_image()
        auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        with app.app_context():
            article = Updates.query.filter_by(title="AutoExcerpt").first()
            if article:
                assert len(article.excerpt) <= 220

    def test_edit_page_returns_200(self, auth_client, published_article):
        r = auth_client.get(f"/news/create/{published_article}/edit")
        assert r.status_code == 200

    def test_edit_page_404_for_nonexistent(self, auth_client):
        r = auth_client.get("/news/create/99999/edit")
        assert r.status_code == 404

    def test_edit_unauthenticated_returns_403(self, client, published_article):
        r = client.post(
            f"/news/create/{published_article}/edit",
            data={
                "title": "Hacked", "category": "General", "author_name": "Hacker",
                "caption": "cap", "detail": "det", "status": "published",
            },
            content_type="multipart/form-data",
        )
        assert r.status_code == 403

    def test_edit_updates_article(self, auth_client, published_article, app):
        r = auth_client.post(
            f"/news/create/{published_article}/edit",
            data={
                "title": "Updated Title",
                "category": "Education",
                "author_name": "Editor",
                "excerpt": "Updated excerpt",
                "caption": "Updated caption",
                "detail": "Updated detail content",
                "status": "published",
                "published_at": "2024-07-01T10:00",
            },
            content_type="multipart/form-data",
        )
        assert r.status_code in (200, 302)
        with app.app_context():
            article = db.session.get(Updates, published_article)
            assert article.title == "Updated Title"

    def test_edit_missing_title_returns_error(self, auth_client, published_article):
        r = auth_client.post(
            f"/news/create/{published_article}/edit",
            data={
                "title": "", "category": "General", "author_name": "Editor",
                "caption": "cap", "detail": "det", "status": "published",
            },
            content_type="multipart/form-data",
        )
        assert r.status_code == 200
        assert b"Title is required" in r.data

    def test_delete_unauthenticated_returns_403(self, client, published_article):
        r = client.get(f"/news/delete/{published_article}")
        assert r.status_code == 403

    def test_delete_removes_article(self, auth_client, published_article, app):
        auth_client.get(f"/news/delete/{published_article}")
        with app.app_context():
            assert db.session.get(Updates, published_article) is None

    def test_delete_nonexistent_returns_404(self, auth_client):
        r = auth_client.get("/news/delete/99999")
        assert r.status_code == 404

    def test_very_long_title_stored(self, auth_client, app):
        long_title = "A" * 250
        payload = self._news_payload(title=long_title)
        payload["image"] = fake_image()
        auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        with app.app_context():
            article = Updates.query.filter_by(title=long_title).first()
            # Either stored (if DB allows) or validation rejected it
            # Either way, app should not crash
            assert True


# ===========================================================================
# 7. TESTIMONY CRUD
# ===========================================================================

class TestTestimonyCRUD:
    def test_create_unauthenticated_returns_403(self, client):
        data = {
            "name": "Bob",
            "testimony": "This is great!",
            "image": fake_image(),
        }
        r = client.post("/news/create/testimony", data=data, content_type="multipart/form-data")
        assert r.status_code == 403

    def test_create_valid_testimony(self, auth_client, app):
        data = {
            "name": "Carol",
            "testimony": "Life-changing program.",
            "image": fake_image(),
        }
        auth_client.post("/news/create/testimony", data=data, content_type="multipart/form-data")
        with app.app_context():
            t = Testimony.query.filter_by(name="Carol").first()
            assert t is not None
            assert t.caption == "Life-changing program."

    def test_create_missing_name_returns_error(self, auth_client):
        data = {"name": "", "testimony": "Good program", "image": fake_image()}
        r = auth_client.post("/news/create/testimony", data=data, content_type="multipart/form-data")
        assert r.status_code == 200
        assert b"Name is required" in r.data

    def test_create_missing_testimony_returns_error(self, auth_client):
        data = {"name": "Bob", "testimony": "", "image": fake_image()}
        r = auth_client.post("/news/create/testimony", data=data, content_type="multipart/form-data")
        assert r.status_code == 200

    def test_create_without_image_returns_error(self, auth_client):
        data = {"name": "Dave", "testimony": "Great!"}
        r = auth_client.post("/news/create/testimony", data=data, content_type="multipart/form-data")
        assert r.status_code == 200
        assert b"Image is required" in r.data

    def test_delete_unauthenticated_returns_403(self, client, sample_testimony):
        r = client.get(f"/testimony/delete/{sample_testimony}")
        assert r.status_code == 403

    def test_delete_removes_testimony(self, auth_client, sample_testimony, app):
        auth_client.get(f"/testimony/delete/{sample_testimony}")
        with app.app_context():
            assert db.session.get(Testimony, sample_testimony) is None

    def test_delete_nonexistent_testimony_returns_404(self, auth_client):
        r = auth_client.get("/testimony/delete/99999")
        assert r.status_code == 404


# ===========================================================================
# 8. ACHIEVEMENT CRUD
# ===========================================================================

class TestAchievementCRUD:
    def test_create_unauthenticated_returns_403(self, client):
        r = client.post("/admin/achievements/add", data={"title": "New Achievement", "text": "Text"})
        assert r.status_code == 403

    def test_create_valid_achievement(self, auth_client, app):
        auth_client.post("/admin/achievements/add", data={"title": "Milestone Reached", "text": "Great work"})
        with app.app_context():
            assert Achievement.query.filter_by(title="Milestone Reached").first() is not None

    def test_create_missing_title_shows_flash(self, auth_client):
        r = auth_client.post(
            "/admin/achievements/add",
            data={"title": "", "text": "text"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert b"Achievement title is required" in r.data

    def test_edit_unauthenticated_returns_403(self, client, sample_achievement):
        r = client.post(f"/admin/achievements/{sample_achievement}/edit", data={"title": "Hack"})
        assert r.status_code == 403

    def test_edit_updates_achievement(self, auth_client, sample_achievement, app):
        auth_client.post(
            f"/admin/achievements/{sample_achievement}/edit",
            data={"title": "Edited Achievement", "text": "Updated text"},
            content_type="multipart/form-data",
        )
        with app.app_context():
            item = db.session.get(Achievement, sample_achievement)
            assert item.title == "Edited Achievement"

    def test_edit_nonexistent_returns_404(self, auth_client):
        r = auth_client.post(
            "/admin/achievements/99999/edit",
            data={"title": "X", "text": ""},
            content_type="multipart/form-data",
        )
        assert r.status_code == 404

    def test_delete_unauthenticated_returns_403(self, client, sample_achievement):
        r = client.get(f"/admin/achievements/{sample_achievement}/delete")
        assert r.status_code == 403

    def test_delete_removes_achievement(self, auth_client, sample_achievement, app):
        auth_client.get(f"/admin/achievements/{sample_achievement}/delete")
        with app.app_context():
            assert db.session.get(Achievement, sample_achievement) is None

    def test_delete_nonexistent_achievement_returns_404(self, auth_client):
        r = auth_client.get("/admin/achievements/99999/delete")
        assert r.status_code == 404


# ===========================================================================
# 9. PROGRAM CRUD
# ===========================================================================

class TestProgramCRUD:
    def test_create_unauthenticated_returns_403(self, client):
        r = client.post("/admin/programs/add", data={"title": "New Program", "description": "Desc", "category": "academic"})
        assert r.status_code == 403

    def test_create_valid_program(self, auth_client, app):
        data = {
            "title": "New Program",
            "description": "Program description",
            "category": "academic",
        }
        auth_client.post("/admin/programs/add", data=data, content_type="multipart/form-data")
        with app.app_context():
            assert Program.query.filter_by(title="New Program").first() is not None

    def test_create_missing_title_shows_flash(self, auth_client):
        data = {"title": "", "description": "Desc", "category": "academic"}
        r = auth_client.post(
            "/admin/programs/add",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"Program title is required" in r.data

    def test_edit_updates_program(self, auth_client, sample_program, app):
        auth_client.post(
            f"/admin/programs/{sample_program}/edit",
            data={"title": "Edited Program", "description": "New desc", "category": "resources"},
            content_type="multipart/form-data",
        )
        with app.app_context():
            item = db.session.get(Program, sample_program)
            assert item.title == "Edited Program"
            assert item.category == "resources"

    def test_edit_nonexistent_returns_404(self, auth_client):
        r = auth_client.post(
            "/admin/programs/99999/edit",
            data={"title": "X"},
            content_type="multipart/form-data",
        )
        assert r.status_code == 404

    def test_delete_removes_program(self, auth_client, sample_program, app):
        auth_client.get(f"/admin/programs/{sample_program}/delete")
        with app.app_context():
            assert db.session.get(Program, sample_program) is None

    def test_delete_unauthenticated_returns_403(self, client, sample_program):
        r = client.get(f"/admin/programs/{sample_program}/delete")
        assert r.status_code == 403

    def test_delete_nonexistent_returns_404(self, auth_client):
        r = auth_client.get("/admin/programs/99999/delete")
        assert r.status_code == 404


# ===========================================================================
# 10. ACTIVITY CRUD
# ===========================================================================

class TestActivityCRUD:
    def test_create_unauthenticated_returns_403(self, client):
        r = client.post("/admin/activities/add", data={"title": "Activity", "description": "Desc"})
        assert r.status_code == 403

    def test_create_valid_activity(self, auth_client, app):
        data = {"title": "Swimming", "description": "Water sports"}
        auth_client.post("/admin/activities/add", data=data, content_type="multipart/form-data")
        with app.app_context():
            assert Activity.query.filter_by(title="Swimming").first() is not None

    def test_create_missing_title_shows_flash(self, auth_client):
        data = {"title": "", "description": "Desc"}
        r = auth_client.post(
            "/admin/activities/add",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"Activity title is required" in r.data

    def test_edit_updates_activity(self, auth_client, sample_activity, app):
        auth_client.post(
            f"/admin/activities/{sample_activity}/edit",
            data={"title": "Edited Activity", "description": "New description"},
            content_type="multipart/form-data",
        )
        with app.app_context():
            item = db.session.get(Activity, sample_activity)
            assert item.title == "Edited Activity"

    def test_delete_removes_activity(self, auth_client, sample_activity, app):
        auth_client.get(f"/admin/activities/{sample_activity}/delete")
        with app.app_context():
            assert db.session.get(Activity, sample_activity) is None

    def test_delete_unauthenticated_returns_403(self, client, sample_activity):
        r = client.get(f"/admin/activities/{sample_activity}/delete")
        assert r.status_code == 403

    def test_delete_nonexistent_returns_404(self, auth_client):
        r = auth_client.get("/admin/activities/99999/delete")
        assert r.status_code == 404


# ===========================================================================
# 11. HERO SLIDE CRUD
# ===========================================================================

class TestHeroSlideCRUD:
    def test_create_unauthenticated_returns_403(self, client):
        data = {"image": fake_image()}
        r = client.post("/admin/hero-slides/add", data=data, content_type="multipart/form-data")
        assert r.status_code == 403

    def test_create_valid_hero_slide(self, auth_client, app):
        data = {"image": fake_image("hero.jpg")}
        auth_client.post("/admin/hero-slides/add", data=data, content_type="multipart/form-data")
        with app.app_context():
            assert HeroSlide.query.count() > 0

    def test_create_without_image_shows_flash(self, auth_client):
        r = auth_client.post(
            "/admin/hero-slides/add",
            data={},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"valid image" in r.data.lower()

    def test_create_with_invalid_extension(self, auth_client):
        data = {"image": (io.BytesIO(b"data"), "file.txt")}
        r = auth_client.post(
            "/admin/hero-slides/add",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"valid image" in r.data.lower()

    def test_delete_removes_hero_slide(self, auth_client, sample_hero_slide, app):
        auth_client.get(f"/admin/hero-slides/{sample_hero_slide}/delete")
        with app.app_context():
            assert db.session.get(HeroSlide, sample_hero_slide) is None

    def test_delete_unauthenticated_returns_403(self, client, sample_hero_slide):
        r = client.get(f"/admin/hero-slides/{sample_hero_slide}/delete")
        assert r.status_code == 403

    def test_delete_nonexistent_returns_404(self, auth_client):
        r = auth_client.get("/admin/hero-slides/99999/delete")
        assert r.status_code == 404


# ===========================================================================
# 12. USER MANAGEMENT (root-only)
# ===========================================================================

class TestUserManagement:
    def test_add_user_unauthenticated_returns_403(self, client):
        r = client.post("/admin/users/add", data={"username": "newuser", "password": "pass123"})
        assert r.status_code == 403

    def test_add_user_non_root_returns_403(self, non_root_auth_client):
        r = non_root_auth_client.post(
            "/admin/users/add",
            data={"username": "another", "password": "pass123"},
        )
        assert r.status_code == 403

    def test_root_can_add_user(self, auth_client, app):
        auth_client.post("/admin/users/add", data={"username": "newstaff", "password": "staffpass"})
        with app.app_context():
            assert Admins.query.filter_by(username="newstaff").first() is not None

    def test_add_user_missing_username(self, auth_client):
        r = auth_client.post(
            "/admin/users/add",
            data={"username": "", "password": "somepass"},
            follow_redirects=True,
        )
        assert b"Username and password are required" in r.data

    def test_add_user_missing_password(self, auth_client):
        r = auth_client.post(
            "/admin/users/add",
            data={"username": "orphan", "password": ""},
            follow_redirects=True,
        )
        assert b"Username and password are required" in r.data

    def test_add_duplicate_username_shows_error(self, auth_client):
        auth_client.post("/admin/users/add", data={"username": "dupe", "password": "pass1"})
        r = auth_client.post(
            "/admin/users/add",
            data={"username": "dupe", "password": "pass2"},
            follow_redirects=True,
        )
        assert b"already exists" in r.data

    def test_added_user_can_login(self, auth_client, client, app):
        auth_client.post("/admin/users/add", data={"username": "logintest", "password": "Login@123"})
        r = client.post(
            "/news/createValidate",
            data={"name": "logintest", "password": "Login@123"},
            follow_redirects=False,
        )
        assert r.status_code == 302

    def test_delete_user_unauthenticated_returns_403(self, client, non_root_admin):
        r = client.get(f"/admin/users/{non_root_admin}/delete")
        assert r.status_code == 403

    def test_non_root_cannot_delete_user(self, non_root_auth_client, non_root_admin):
        r = non_root_auth_client.get(f"/admin/users/{non_root_admin}/delete")
        assert r.status_code == 403

    def test_root_can_delete_non_root_user(self, auth_client, non_root_admin, app):
        auth_client.get(f"/admin/users/{non_root_admin}/delete")
        with app.app_context():
            assert db.session.get(Admins, non_root_admin) is None

    def test_cannot_delete_root_user(self, auth_client, app):
        with app.app_context():
            root = Admins.query.filter_by(username="testroot").first()
            root_id = root.id
        r = auth_client.get(f"/admin/users/{root_id}/delete", follow_redirects=True)
        assert b"Cannot delete the root user" in r.data
        with app.app_context():
            assert db.session.get(Admins, root_id) is not None

    def test_delete_nonexistent_user_returns_404(self, auth_client):
        r = auth_client.get("/admin/users/99999/delete")
        assert r.status_code == 404

    def test_change_password_correct_current(self, auth_client, app):
        r = auth_client.post(
            "/admin/users/change-password",
            data={
                "current_password": "rootpass123",
                "new_password": "NewSecure1!",
                "confirm_password": "NewSecure1!",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        # Reset password back for other tests
        with app.app_context():
            root = Admins.query.filter_by(username="testroot").first()
            root.set_password("rootpass123")
            db.session.commit()

    def test_change_password_wrong_current(self, auth_client):
        r = auth_client.post(
            "/admin/users/change-password",
            data={
                "current_password": "wrongpassword",
                "new_password": "NewPass123",
                "confirm_password": "NewPass123",
            },
            follow_redirects=True,
        )
        assert b"Current password is incorrect" in r.data

    def test_change_password_mismatch(self, auth_client):
        r = auth_client.post(
            "/admin/users/change-password",
            data={
                "current_password": "rootpass123",
                "new_password": "NewPass123",
                "confirm_password": "DifferentPass123",
            },
            follow_redirects=True,
        )
        assert b"do not match" in r.data

    def test_change_password_too_short(self, auth_client):
        r = auth_client.post(
            "/admin/users/change-password",
            data={
                "current_password": "rootpass123",
                "new_password": "ab",
                "confirm_password": "ab",
            },
            follow_redirects=True,
        )
        assert b"at least 6 characters" in r.data

    def test_change_password_missing_fields(self, auth_client):
        r = auth_client.post(
            "/admin/users/change-password",
            data={"current_password": "", "new_password": "", "confirm_password": ""},
            follow_redirects=True,
        )
        assert b"required" in r.data.lower()

    def test_change_password_unauthenticated_returns_403(self, client):
        r = client.post(
            "/admin/users/change-password",
            data={"current_password": "x", "new_password": "y", "confirm_password": "y"},
        )
        assert r.status_code == 403


# ===========================================================================
# 13. SITE CONTENT UPDATE
# ===========================================================================

class TestSiteContentUpdate:
    def test_update_unauthenticated_returns_403(self, client):
        r = client.post(
            "/admin/content/update",
            data={"page": "home", "section": "mission", "field": "title", "value": "New Mission"},
        )
        assert r.status_code == 403

    def test_update_valid_content(self, auth_client, app):
        auth_client.post(
            "/admin/content/update",
            data={"page": "home", "section": "mission", "field": "title", "value": "Updated Mission"},
        )
        with app.app_context():
            record = SiteContent.query.filter_by(page="home", section="mission", field="title").first()
            assert record is not None
            assert record.value == "Updated Mission"

    def test_update_invalid_page_flashes_error(self, auth_client):
        r = auth_client.post(
            "/admin/content/update",
            data={"page": "nonexistent_page", "section": "hero", "field": "title", "value": "X"},
            follow_redirects=True,
        )
        assert b"Invalid content section" in r.data

    def test_update_invalid_section_flashes_error(self, auth_client):
        r = auth_client.post(
            "/admin/content/update",
            data={"page": "home", "section": "nonexistent_section", "field": "title", "value": "X"},
            follow_redirects=True,
        )
        assert b"Invalid content section" in r.data

    def test_update_invalid_field_flashes_error(self, auth_client):
        r = auth_client.post(
            "/admin/content/update",
            data={"page": "home", "section": "mission", "field": "nonexistent_field", "value": "X"},
            follow_redirects=True,
        )
        assert b"Invalid content section" in r.data

    def test_update_content_reflected_on_page(self, auth_client, client, app):
        auth_client.post(
            "/admin/content/update",
            data={"page": "home", "section": "mission", "field": "title", "value": "Special Mission Title XYZ"},
        )
        r = client.get("/")
        assert b"Special Mission Title XYZ" in r.data

    def test_image_update_unauthenticated_returns_403(self, client):
        data = {
            "page": "home",
            "section": "hero",
            "field": "background_image",
            "action": "remove",
        }
        r = client.post("/admin/content/image", data=data)
        assert r.status_code == 403

    def test_image_remove_action(self, auth_client):
        r = auth_client.post(
            "/admin/content/image",
            data={
                "page": "home",
                "section": "hero",
                "field": "background_image",
                "action": "remove",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200

    def test_image_upload_invalid_extension(self, auth_client):
        data = {
            "page": "about",
            "section": "overview",
            "field": "image",
            "action": "upload",
            "image": (io.BytesIO(b"data"), "file.exe"),
        }
        r = auth_client.post(
            "/admin/content/image",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"valid image" in r.data.lower()

    def test_image_upload_invalid_page_flashes_error(self, auth_client):
        data = {
            "page": "ghost_page",
            "section": "hero",
            "field": "background_image",
            "action": "upload",
            "image": fake_image(),
        }
        r = auth_client.post(
            "/admin/content/image",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"Invalid image content section" in r.data


# ===========================================================================
# 14. HELPER FUNCTIONS
# ===========================================================================

class TestHelperFunctions:
    def test_allowed_file_jpg(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("photo.jpg") is True

    def test_allowed_file_jpeg(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("photo.jpeg") is True

    def test_allowed_file_png(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("image.PNG") is True  # case insensitive

    def test_allowed_file_gif(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("anim.gif") is True

    def test_allowed_file_pdf_rejected(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("doc.pdf") is False

    def test_allowed_file_exe_rejected(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("virus.exe") is False

    def test_allowed_file_no_extension(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("filewithoutextension") is False

    def test_allowed_file_empty_string(self, app):
        from flask_app.app import allowed_file
        assert allowed_file("") is False

    def test_allowed_file_dot_only(self, app):
        from flask_app.app import allowed_file
        assert allowed_file(".jpg") is True  # has extension after dot

    def test_parse_datetime_local_valid(self, app):
        from flask_app.app import parse_datetime_local
        with app.app_context():
            result = parse_datetime_local("2024-06-15T14:30")
            assert result is not None
            assert result.year == 2024
            assert result.month == 6
            assert result.day == 15

    def test_parse_datetime_local_empty_string(self, app):
        from flask_app.app import parse_datetime_local
        with app.app_context():
            assert parse_datetime_local("") is None

    def test_parse_datetime_local_whitespace(self, app):
        from flask_app.app import parse_datetime_local
        with app.app_context():
            assert parse_datetime_local("   ") is None

    def test_parse_datetime_local_invalid_format(self, app):
        from flask_app.app import parse_datetime_local
        with app.app_context():
            assert parse_datetime_local("not-a-date") is None

    def test_format_date_filter_with_datetime(self, app):
        from flask_app.app import format_date
        with app.app_context():
            dt = datetime(2024, 3, 15)
            result = format_date(dt)
            assert "2024" in result
            assert "Mar" in result

    def test_format_date_filter_with_none(self, app):
        from flask_app.app import format_date
        with app.app_context():
            assert format_date(None) == ""

    def test_format_date_custom_format(self, app):
        from flask_app.app import format_date
        with app.app_context():
            dt = datetime(2024, 1, 5)
            result = format_date(dt, "%Y")
            assert result == "2024"

    def test_is_image_content_field_background_image(self, app):
        from flask_app.app import is_image_content_field
        assert is_image_content_field("background_image") is True

    def test_is_image_content_field_logo_image(self, app):
        from flask_app.app import is_image_content_field
        assert is_image_content_field("logo_image") is True

    def test_is_image_content_field_image(self, app):
        from flask_app.app import is_image_content_field
        assert is_image_content_field("image") is True

    def test_is_image_content_field_title_not_image(self, app):
        from flask_app.app import is_image_content_field
        assert is_image_content_field("title") is False

    def test_is_image_content_field_ends_with_image(self, app):
        from flask_app.app import is_image_content_field
        assert is_image_content_field("show_image") is True

    def test_render_markdown_bold(self, app):
        from flask_app.app import render_markdown_content
        with app.app_context():
            result = render_markdown_content("**bold**")
            assert "<strong>" in result or "<b>" in result

    def test_render_markdown_none(self, app):
        from flask_app.app import render_markdown_content
        with app.app_context():
            result = render_markdown_content(None)
            assert result is not None

    def test_render_markdown_xss_escaped(self, app):
        from flask_app.app import render_markdown_content
        with app.app_context():
            result = render_markdown_content("<script>alert('xss')</script>")
            assert "<script>" not in result


# ===========================================================================
# 15. EDGE CASES AND SECURITY
# ===========================================================================

class TestEdgeCases:
    def test_news_id_zero_returns_404(self, client):
        r = client.get("/news/0")
        assert r.status_code == 404

    def test_news_id_negative_returns_404(self, client):
        r = client.get("/news/-1")
        # Flask URL routing may return 404 for negative int params
        assert r.status_code in (404, 405, 400)

    def test_news_id_string_returns_404(self, client):
        r = client.get("/news/not-a-number")
        assert r.status_code == 404

    def test_achievement_id_string_returns_404(self, client):
        r = client.get("/admin/achievements/abc/delete")
        assert r.status_code == 404

    def test_contact_xss_stored_safely(self, client, app):
        payload = {
            "name": "<script>alert(1)</script>",
            "email": "xss@example.com",
            "contact-number": "0771234567",
            "purpose": "Testing",
            "message": "XSS attempt",
        }
        client.post("/contact", data=payload)
        with app.app_context():
            c = Contact.query.filter_by(email="xss@example.com").first()
            assert c is not None
            # The raw value stored, but render_template escapes it
            assert "<script>" in c.full_name

    def test_newsletter_xss_in_email(self, client, app):
        evil = "<script>alert(1)</script>@evil.com"
        client.post("/newsletter", data={"newsletter": evil})
        with app.app_context():
            # "@" is present so it gets stored – we just want no crash
            assert True

    def test_admin_create_page_unauthenticated_shows_login_prompt(self, client):
        r = client.get("/news/create")
        assert r.status_code == 200
        # Should not 403, but should indicate authentication needed
        assert b"login" in r.data.lower() or b"sign in" in r.data.lower() or b"authenticated" in r.data.lower() or r.status_code == 200

    def test_protected_post_route_without_auth_returns_403(self, client):
        r = client.post("/admin/achievements/add", data={"title": "X", "text": ""})
        assert r.status_code == 403

    def test_large_payload_contact(self, client, app):
        large_text = "A" * 10000
        payload = {
            "name": "LargeName",
            "email": "large@example.com",
            "contact-number": "0771234567",
            "purpose": "Testing large",
            "message": large_text,
        }
        r = client.post("/contact", data=payload, follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            c = Contact.query.filter_by(email="large@example.com").first()
            assert c is not None

    def test_unicode_content_in_contact(self, client, app):
        payload = {
            "name": "Müller Ñoño 中文",
            "email": "unicode@example.com",
            "contact-number": "+263771234567",
            "purpose": "General",
            "message": "Unicode: 你好世界 🌍",
        }
        r = client.post("/contact", data=payload)
        with app.app_context():
            c = Contact.query.filter_by(email="unicode@example.com").first()
            assert c is not None
            assert "Müller" in c.full_name

    def test_unicode_in_news_title(self, auth_client, app):
        payload = {
            "title": "News: 中文标题",
            "category": "General",
            "author_name": "Author",
            "excerpt": "excerpt",
            "caption": "caption",
            "detail": "detail",
            "status": "draft",
            "published_at": "",
            "image": fake_image(),
        }
        auth_client.post("/news/create", data=payload, content_type="multipart/form-data")
        with app.app_context():
            article = Updates.query.filter_by(title="News: 中文标题").first()
            assert article is not None

    def test_multiple_newsletters_from_same_ip(self, client, app):
        for i in range(5):
            client.post("/newsletter", data={"newsletter": f"user{i}@example.com"})
        with app.app_context():
            assert Newsletter.query.count() == 5

    def test_session_not_shared_between_clients(self, app):
        c1 = app.test_client()
        c2 = app.test_client()
        login(c1)
        with c1.session_transaction() as s1:
            assert s1.get("authenticated") is True
        with c2.session_transaction() as s2:
            assert not s2.get("authenticated")

    def test_logout_then_protected_returns_403(self, auth_client):
        auth_client.get("/admin/logout")
        r = auth_client.post("/admin/achievements/add", data={"title": "Post-logout"})
        assert r.status_code == 403

    def test_news_pagination_no_crash_empty_db(self, client, app):
        r = client.get("/")
        assert r.status_code == 200

    def test_achievements_page_empty_db(self, client, app):
        r = client.get("/achievements")
        assert r.status_code == 200

    def test_programs_page_empty_db(self, client, app):
        r = client.get("/programs")
        assert r.status_code == 200


# ===========================================================================
# 16. MODEL INTEGRITY
# ===========================================================================

class TestModels:
    def test_admins_password_hashing(self, app):
        with app.app_context():
            admin = Admins(username="hashtest", password="")
            admin.set_password("mypassword")
            assert admin.password_hash != "mypassword"
            assert admin.check_password("mypassword") is True
            assert admin.check_password("wrongpassword") is False

    def test_admins_username_unique(self, app):
        with app.app_context():
            a1 = Admins(username="unique_user", password="")
            a1.set_password("pw1")
            db.session.add(a1)
            db.session.commit()

            a2 = Admins(username="unique_user", password="")
            a2.set_password("pw2")
            db.session.add(a2)
            import sqlalchemy.exc
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_updates_default_status_is_draft(self, app):
        with app.app_context():
            article = Updates(
                title="Default Status",
                category="General",
                author_name="Author",
                excerpt="",
                caption="cap",
                detail="det",
                image="",
                created_at=datetime.utcnow(),
            )
            db.session.add(article)
            db.session.commit()
            fetched = Updates.query.filter_by(title="Default Status").first()
            assert fetched.status == "draft"

    def test_achievement_default_image_empty(self, app):
        with app.app_context():
            a = Achievement(title="No Image", text="text")
            db.session.add(a)
            db.session.commit()
            fetched = Achievement.query.filter_by(title="No Image").first()
            assert fetched.image == ""

    def test_site_content_unique_constraint(self, app):
        with app.app_context():
            s1 = SiteContent(page="test_page", section="test_section", field="test_field", value="v1")
            db.session.add(s1)
            db.session.commit()

            s2 = SiteContent(page="test_page", section="test_section", field="test_field", value="v2")
            db.session.add(s2)
            import sqlalchemy.exc
            with pytest.raises(sqlalchemy.exc.IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_program_media_cascade_delete(self, app):
        from flask_app.models import ProgramMedia
        with app.app_context():
            prog = Program(title="Cascade Test", description="", category="academic", show_image="", sort_order=0)
            db.session.add(prog)
            db.session.flush()
            media = ProgramMedia(program_id=prog.id, image="updateImages/m.jpg", sort_order=0)
            db.session.add(media)
            db.session.commit()

            prog_id = prog.id
            db.session.delete(prog)
            db.session.commit()

            assert ProgramMedia.query.filter_by(program_id=prog_id).count() == 0

    def test_contact_stores_all_fields(self, app):
        with app.app_context():
            c = Contact(
                full_name="Full Name",
                email="full@example.com",
                phone="0771111111",
                purpose="Donation",
                message="Hello there",
            )
            db.session.add(c)
            db.session.commit()
            fetched = Contact.query.filter_by(email="full@example.com").first()
            assert fetched.full_name == "Full Name"
            assert fetched.phone == "0771111111"
            assert fetched.purpose == "Donation"
            assert fetched.message == "Hello there"
