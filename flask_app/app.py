from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import markdown
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_
from markupsafe import Markup, escape
from werkzeug.utils import secure_filename

from db_migrations import run_migrations
from models import Contact, Newsletter, SiteContent, Testimony, Updates, db

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"
UPLOAD_DIR = PUBLIC_DIR / "updateImages"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

app = Flask(
    __name__,
    static_folder=str(PUBLIC_DIR),
    static_url_path="",
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.sqlite3'}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

db.init_app(app)


@app.template_filter("format_date")
def format_date(value: datetime | None, fmt: str = "%a, %d %b %Y") -> str:
    if not value:
        return ""
    return value.strftime(fmt)


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_authenticated() -> bool:
    return bool(session.get("authenticated"))


def admin_credentials() -> tuple[str, str]:
    name = os.getenv("ADMIN_NAME", "tweenstongogara")
    password = os.getenv("ADMIN_PASSWORD", "tweens@2020Admin")
    return name, password


SITE_CONTENT_DEFAULTS = {
    "global": {
        "branding": {
            "org_name": "Tweens",
            "donate_url": "https://www.globalgiving.org/projects/transformative-education-for-refugees-in-zimbabwe/",
            "logo_image": "images/logo.png",
        },
        "footer": {
            "tagline": "Refugee-led education initiatives building brighter futures through mentorship, access, and community care.",
            "newsletter_title": "News Letter",
            "newsletter_caption": "Enter your email to signup for our newsletter.",
            "copyright_year": "2025",
        },
    },
    "home": {
        "hero": {
            "title": "Tweens",
            "caption": "Over five years of improving the lives of children living in Tongogara refugee settlement.",
            "background_image": "images/home1.png",
        },
        "mission": {
            "title": "Our Mission",
            "body": "To empower underprivileged students by providing educational support, essential resources, and meaningful community engagement, fostering a culture of continuous learning, resilience, and personal growth.",
        },
        "values": {
            "title": "Our Values",
            "body": "Education for Empowerment, Inclusivity and Equality, and Community Collaboration.",
        },
        "impact": {
            "title": "Our Impact",
            "body": "TWEENS has significantly impacted underprivileged students through education and community support. Up to 200 students benefit from tutoring, study spaces, Wi-Fi, and learning materials.",
        },
        "sections": {
            "activities_title": "Our Activities",
            "partners_title": "Our Partners",
            "news_title": "News",
        },
    },
    "about": {
        "hero": {
            "topic": "About",
            "caption": "Learn about Tweens",
            "background_image": "images/about_hero.JPG",
        },
        "overview": {
            "title": "Who We Are",
            "body": "Together We Educationally Empower Non-privileged Students (TWEENS) is a program aimed at supporting refugee youth in Tongogara Refugee Settlement, backed by Education Matters' mission to connect talent with opportunity. TWEENS is a refugee-led peer tutoring initiative focused on empowering refugee youth through education and mentorship.",
            "image": "images/aboutWhoWeAre.png",
        },
        "mission": {"body": "Promote education in Tongogara Refugee Settlement by offering quality learning opportunities, resources, and mentorship for refugee youth."},
        "vision": {"body": "Empower local and refugee youth by providing access to quality education and mentorship, helping them develop skills and confidence needed to pursue their dreams."},
        "values": {"body": "Education for empowerment, inclusivity, equality, and community collaboration to create sustainable impact."},
        "background": {
            "title": "Background",
            "body": "The TWEENS project in Tongogara Refugee Settlement was created to support academically talented refugees who lack the intellectual resources and counseling to continue their education beyond O-levels.",
        },
    },
    "achievements": {
        "hero": {
            "topic": "Achievements",
            "caption": "Learn about our achievements",
            "background_image": "images/achieveHero.png",
        },
        "overview": {
            "title": "Our Achievements",
            "caption": "Tap a star to explore the stories behind our milestones. Each highlight represents a student, a community, or a breakthrough powered by collective action.",
        },
        "testimonials": {"title": "Testimonials"},
    },
    "contact": {
        "hero": {
            "topic": "Contact Us",
            "caption": "Get in touch",
            "background_image": "images/contactHero.png",
        },
        "form": {
            "title": "Get In Touch",
            "caption": "We respond within 48 hours. Tell us how we can help.",
            "image": "images/contactGetInTouch.png",
        },
        "direct": {
            "title": "Direct Contact",
            "phone": "078 767 6946",
            "email": "admin@tweenstongogara.org",
            "location": "We are located in Tongogara Refugee Settlement, Zimbabwe.",
        },
    },
    "programs": {
        "hero": {
            "topic": "Programs",
            "caption": "Explore our programs",
            "background_image": "images/tutoring.JPG",
        },
        "overview": {"title": "Program Highlights"},
        "cta": {
            "title": "Call To Action",
            "body": "Do you want to volunteer to any of our programs? Feel free to contact us on our contact page.",
            "button": "Volunteer",
        },
    },
    "donations": {
        "hero": {
            "topic": "Donations",
            "caption": "Support our work",
            "background_image": "images/achieveHero.png",
        },
        "overview": {
            "title": "Support TWEENS",
            "body": "Your donation helps provide education, mentorship, and resources for refugee youth.",
            "button": "Donate on GlobalGiving",
        },
    },
}


def humanize(value: str) -> str:
    return value.replace("_", " ").strip().title()


def is_image_content_field(field_name: str) -> bool:
    return field_name in {"image", "background_image", "logo_image"} or field_name.endswith("_image")


NEWS_STATUSES = {"draft", "published"}


def parse_datetime_local(value: str) -> datetime | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def public_news_query():
    return Updates.query.filter(
        Updates.status == "published",
        or_(Updates.published_at.is_(None), Updates.published_at <= datetime.utcnow()),
    )


def render_markdown_content(value: str | None) -> Markup:
    source = str(escape(value or ""))
    html = markdown.markdown(
        source,
        extensions=["fenced_code", "tables", "sane_lists", "nl2br"],
    )
    return Markup(html)


def seed_site_content() -> None:
    existing = {
        (item.page, item.section, item.field)
        for item in SiteContent.query.with_entities(SiteContent.page, SiteContent.section, SiteContent.field).all()
    }
    rows_to_add = []
    for page, sections in SITE_CONTENT_DEFAULTS.items():
        for section, fields in sections.items():
            for field, default_value in fields.items():
                key = (page, section, field)
                if key in existing:
                    continue
                rows_to_add.append(
                    SiteContent(
                        page=page,
                        section=section,
                        field=field,
                        value=default_value,
                    )
                )

    if rows_to_add:
        db.session.add_all(rows_to_add)
        db.session.commit()


def get_page_content(page: str) -> dict[str, dict[str, str]]:
    defaults = SITE_CONTENT_DEFAULTS.get(page, {})
    content = {section: dict(fields) for section, fields in defaults.items()}
    rows = SiteContent.query.filter_by(page=page).all()
    for row in rows:
        content.setdefault(row.section, {})[row.field] = row.value
    return content


def get_site_content_editor() -> dict[str, list[dict[str, object]]]:
    values = {
        (row.page, row.section, row.field): row.value
        for row in SiteContent.query.with_entities(
            SiteContent.page,
            SiteContent.section,
            SiteContent.field,
            SiteContent.value,
        ).all()
    }

    editor = {}
    for page, sections in SITE_CONTENT_DEFAULTS.items():
        page_sections = []
        for section, fields in sections.items():
            section_fields = []
            for field, default_value in fields.items():
                section_fields.append(
                    {
                        "name": field,
                        "label": humanize(field),
                        "value": values.get((page, section, field), default_value),
                        "is_image": is_image_content_field(field),
                    }
                )
            page_sections.append(
                {
                    "name": section,
                    "label": humanize(section),
                    "fields": section_fields,
                }
            )
        editor[page] = page_sections
    return editor


with app.app_context():
    run_migrations()
    db.create_all()
    seed_site_content()


@app.context_processor
def inject_global_site_content():
    global_content = get_page_content("global")
    return {
        "global_content": global_content.get("branding", {}),
        "footer_content": global_content.get("footer", {}),
    }


@app.get("/")
def home():
    updates = public_news_query().order_by(func.coalesce(Updates.published_at, Updates.created_at).desc(), Updates.id.desc()).all()
    return render_template(
        "home.html",
        updates=updates,
        page_content=get_page_content("home"),
        file_js=f'<script src="{url_for("static", filename="myJS/home.js")}"></script>',
    )


@app.post("/newsletter")
def newsletter_signup():
    email = request.form.get("newsletter", "").strip()
    if not email or "@" not in email:
        flash("Please enter a valid email.", "newsletter_error")
        return redirect(request.referrer or url_for("home"))

    db.session.add(Newsletter(email=email))
    db.session.commit()
    flash("Email sent successfully!", "newsletter_success")
    return redirect(request.referrer or url_for("home"))


@app.get("/news/create")
def news_create_page():
    news = Updates.query.order_by(Updates.id.desc()).all()
    contacts = Contact.query.order_by(Contact.id.desc()).all()
    newsletters = Newsletter.query.order_by(Newsletter.id.desc()).all()
    testimonies = Testimony.query.order_by(Testimony.id.desc()).all()
    return render_template(
        "add_updates.html",
        authenticated=is_authenticated(),
        news=news,
        contacts=contacts,
        newsletters=newsletters,
        testimonies=testimonies,
        site_content_editor=get_site_content_editor(),
    )


@app.post("/admin/content/update")
def admin_content_update():
    if not is_authenticated():
        abort(403)

    page = request.form.get("page", "").strip()
    section = request.form.get("section", "").strip()
    field = request.form.get("field", "").strip()
    value = request.form.get("value", "").strip()

    if (
        page not in SITE_CONTENT_DEFAULTS
        or section not in SITE_CONTENT_DEFAULTS.get(page, {})
        or field not in SITE_CONTENT_DEFAULTS.get(page, {}).get(section, {})
    ):
        flash("Invalid content section selected.", "content_error")
        return redirect(url_for("news_create_page"))

    record = SiteContent.query.filter_by(page=page, section=section, field=field).first()
    if record:
        record.value = value
    else:
        db.session.add(SiteContent(page=page, section=section, field=field, value=value))

    db.session.commit()
    flash("Page content updated.", "content_success")
    return redirect(url_for("news_create_page"))


@app.post("/admin/content/image")
def admin_content_image_update():
    if not is_authenticated():
        abort(403)

    page = request.form.get("page", "").strip()
    section = request.form.get("section", "").strip()
    field = request.form.get("field", "").strip()
    action = request.form.get("action", "upload").strip()

    if (
        page not in SITE_CONTENT_DEFAULTS
        or section not in SITE_CONTENT_DEFAULTS.get(page, {})
        or field not in SITE_CONTENT_DEFAULTS.get(page, {}).get(section, {})
        or not is_image_content_field(field)
    ):
        flash("Invalid image content section selected.", "content_error")
        return redirect(url_for("news_create_page"))

    record = SiteContent.query.filter_by(page=page, section=section, field=field).first()
    current_value = record.value if record else SITE_CONTENT_DEFAULTS[page][section][field]

    if action == "remove":
        if current_value.startswith("updateImages/"):
            current_path = PUBLIC_DIR / current_value
            if current_path.exists():
                current_path.unlink()

        default_value = SITE_CONTENT_DEFAULTS[page][section][field]
        if record:
            record.value = default_value
        else:
            db.session.add(SiteContent(page=page, section=section, field=field, value=default_value))

        db.session.commit()
        flash("Image removed and reset to default.", "content_success")
        return redirect(url_for("news_create_page"))

    image = request.files.get("image")
    if not image or not image.filename or not allowed_file(image.filename):
        flash("Please upload a valid image (jpg, jpeg, png, gif).", "content_error")
        return redirect(url_for("news_create_page"))

    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
    image_relative_path = f"updateImages/{filename}"
    image.save(UPLOAD_DIR / filename)

    if current_value.startswith("updateImages/"):
        current_path = PUBLIC_DIR / current_value
        if current_path.exists():
            current_path.unlink()

    if record:
        record.value = image_relative_path
    else:
        db.session.add(SiteContent(page=page, section=section, field=field, value=image_relative_path))

    db.session.commit()
    flash("Image updated successfully.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/news/createValidate")
def news_validate_page():
    return render_template("create_validate.html")


@app.post("/news/createValidate")
def news_validate_submit():
    name = request.form.get("name", "")
    password = request.form.get("password", "")
    admin_name, admin_password = admin_credentials()

    # if name == admin_name and password == admin_password:
    if name == "tweens" and password == "tweens":
        session["authenticated"] = True
        return redirect(url_for("news_create_page"))

    session["authenticated"] = False
    return redirect(url_for("home"))


@app.post("/news/create")
def news_create():
    if not is_authenticated():
        abort(403)

    title = request.form.get("title", "").strip()
    category = request.form.get("category", "General").strip()
    author_name = request.form.get("author_name", "Tweens Admin").strip()
    excerpt = request.form.get("excerpt", "").strip()
    caption = request.form.get("caption", "").strip()
    detail = request.form.get("detail", "").strip()
    status = request.form.get("status", "draft").strip().lower()
    published_at_raw = request.form.get("published_at", "")
    published_at = parse_datetime_local(published_at_raw)
    image = request.files.get("image")
    errors = {}

    if not title:
        errors["title"] = "Title is required."
    if not category:
        errors["category"] = "Category is required."
    if not author_name:
        errors["author_name"] = "Author is required."
    if not caption:
        errors["caption"] = "Caption is required."
    if not detail:
        errors["detail"] = "Detail is required."
    if status not in NEWS_STATUSES:
        errors["status"] = "Status must be draft or published."
    if published_at_raw.strip() and not published_at:
        errors["published_at"] = "Publish date/time is invalid."
    if not image or not allowed_file(image.filename):
        errors["image"] = "Image is required (jpg, jpeg, png, gif)."

    if status == "published" and not published_at:
        published_at = datetime.utcnow()

    if not excerpt:
        excerpt = detail[:220]

    if errors:
        news = Updates.query.order_by(Updates.id.desc()).all()
        contacts = Contact.query.order_by(Contact.id.desc()).all()
        newsletters = Newsletter.query.order_by(Newsletter.id.desc()).all()
        testimonies = Testimony.query.order_by(Testimony.id.desc()).all()
        return render_template(
            "add_updates.html",
            authenticated=True,
            news=news,
            contacts=contacts,
            newsletters=newsletters,
            testimonies=testimonies,
            site_content_editor=get_site_content_editor(),
            news_form_data={
                "title": title,
                "category": category,
                "author_name": author_name,
                "excerpt": excerpt,
                "caption": caption,
                "detail": detail,
                "status": status,
                "published_at": published_at_raw,
            },
            errors=errors,
        )

    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
    image_path = f"updateImages/{filename}"
    image.save(UPLOAD_DIR / filename)

    update = Updates(
        title=title,
        category=category,
        author_name=author_name,
        excerpt=excerpt,
        detail=detail,
        caption=caption,
        image=image_path,
        status=status,
        published_at=published_at,
        created_at=datetime.utcnow(),
    )
    db.session.add(update)
    db.session.commit()

    return redirect(url_for("home"))


@app.post("/news/create/testimony")
def testimony_create():
    if not is_authenticated():
        abort(403)

    name = request.form.get("name", "").strip()
    testimony = request.form.get("testimony", "").strip()
    image = request.files.get("image")
    errors = {}

    if not name:
        errors["name"] = "Name is required."
    if not testimony:
        errors["testimony"] = "Testimony is required."
    if not image or not allowed_file(image.filename):
        errors["image"] = "Image is required (jpg, jpeg, png, gif)."

    if errors:
        news = Updates.query.order_by(Updates.id.desc()).all()
        contacts = Contact.query.order_by(Contact.id.desc()).all()
        newsletters = Newsletter.query.order_by(Newsletter.id.desc()).all()
        testimonies = Testimony.query.order_by(Testimony.id.desc()).all()
        return render_template(
            "add_updates.html",
            authenticated=True,
            news=news,
            contacts=contacts,
            newsletters=newsletters,
            testimonies=testimonies,
            site_content_editor=get_site_content_editor(),
            errors=errors,
        )

    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
    image_path = f"updateImages/{filename}"
    image.save(UPLOAD_DIR / filename)

    db.session.add(Testimony(name=name, image=image_path, caption=testimony))
    db.session.commit()

    return redirect(url_for("achievements"))


@app.get("/testimony/delete/<int:testimony_id>")
def testimony_delete(testimony_id: int):
    if not is_authenticated():
        abort(403)

    testimony = Testimony.query.get_or_404(testimony_id)
    db.session.delete(testimony)
    db.session.commit()
    return redirect(url_for("news_create_page"))


@app.get("/news/create/<int:update_id>/edit")
def news_edit_page(update_id: int):
    update = Updates.query.get_or_404(update_id)
    return render_template("edit_updates.html", authenticated=is_authenticated(), update=update)


@app.post("/news/create/<int:update_id>/edit")
def news_edit(update_id: int):
    if not is_authenticated():
        abort(403)

    update = Updates.query.get_or_404(update_id)
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "General").strip()
    author_name = request.form.get("author_name", "Tweens Admin").strip()
    excerpt = request.form.get("excerpt", "").strip()
    caption = request.form.get("caption", "").strip()
    detail = request.form.get("detail", "").strip()
    status = request.form.get("status", "draft").strip().lower()
    published_at_raw = request.form.get("published_at", "")
    published_at = parse_datetime_local(published_at_raw)
    image = request.files.get("image")

    errors = {}
    if not title:
        errors["title"] = "Title is required."
    if not category:
        errors["category"] = "Category is required."
    if not author_name:
        errors["author_name"] = "Author is required."
    if not caption:
        errors["caption"] = "Caption is required."
    if not detail:
        errors["detail"] = "Detail is required."
    if status not in NEWS_STATUSES:
        errors["status"] = "Status must be draft or published."
    if published_at_raw.strip() and not published_at:
        errors["published_at"] = "Publish date/time is invalid."
    if image and not allowed_file(image.filename):
        errors["image"] = "Image must be jpg, jpeg, png, or gif."

    if status == "published" and not published_at:
        published_at = datetime.utcnow()

    if not excerpt:
        excerpt = detail[:220]

    if errors:
        return render_template(
            "edit_updates.html",
            authenticated=True,
            update=update,
            errors=errors,
        )

    if image and image.filename:
        filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
        image_path = f"updateImages/{filename}"
        image.save(UPLOAD_DIR / filename)

        if update.image:
            old_path = PUBLIC_DIR / update.image
            if old_path.exists():
                old_path.unlink()

        update.image = image_path

    update.title = title
    update.category = category
    update.author_name = author_name
    update.excerpt = excerpt
    update.caption = caption
    update.detail = detail
    update.status = status
    update.published_at = published_at
    db.session.commit()

    flash("News update edited successfully!", "news_success")
    return redirect(url_for("home"))


@app.get("/news/delete/<int:update_id>")
def news_delete(update_id: int):
    if not is_authenticated():
        abort(403)

    update = Updates.query.get_or_404(update_id)
    db.session.delete(update)
    db.session.commit()
    return redirect(url_for("news_create_page"))


@app.get("/news/<int:update_id>")
def news_detail(update_id: int):
    query = Updates.query
    if not is_authenticated():
        query = public_news_query()

    update = query.filter(Updates.id == update_id).first_or_404()
    newer_update = query.filter(Updates.id > update.id).order_by(Updates.id.asc()).first()
    older_update = query.filter(Updates.id < update.id).order_by(Updates.id.desc()).first()
    related_updates = (
        query.filter(Updates.id != update.id)
        .order_by(func.coalesce(Updates.published_at, Updates.created_at).desc(), Updates.id.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "news.html",
        update=update,
        newer_update=newer_update,
        older_update=older_update,
        related_updates=related_updates,
        rendered_detail=render_markdown_content(update.detail),
        file_js="",
    )


@app.get("/about")
def about():
    return render_template(
        "about.html",
        page_content=get_page_content("about"),
        file_js=f'<script src="{url_for("static", filename="myJS/about.js")}"></script>',
    )


@app.get("/achievements")
def achievements():
    testimonies = Testimony.query.order_by(Testimony.id.desc()).all()
    return render_template(
        "achievements.html",
        testimonies=testimonies,
        page_content=get_page_content("achievements"),
        file_js=f'<script src="{url_for("static", filename="myJS/achievements.js")}"></script>',
    )


@app.get("/contact")
def contact():
    return render_template(
        "contact.html",
        page_content=get_page_content("contact"),
        file_js=f'<script src="{url_for("static", filename="myJS/contact.js")}"></script>',
    )


@app.post("/contact")
def contact_submit():
    data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "contact_number": request.form.get("contact-number", "").strip(),
        "purpose": request.form.get("purpose", "").strip(),
        "message": request.form.get("message", "").strip(),
    }
    errors = {}
    if not data["name"]:
        errors["name"] = "Name is required."
    if not data["email"] or "@" not in data["email"]:
        errors["email"] = "Valid email is required."
    if not data["contact_number"]:
        errors["contact-number"] = "Contact number is required."
    if not data["purpose"]:
        errors["purpose"] = "Purpose is required."
    if not data["message"]:
        errors["message"] = "Message is required."

    if errors:
        return render_template(
            "contact.html",
            errors=errors,
            form_data=data,
            page_content=get_page_content("contact"),
            file_js=(
                f'<script src="{url_for("static", filename="myJS/contact.js")}"></script>'
                '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js" '
                'integrity="sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy" '
                'crossorigin="anonymous"></script>'
            ),
        )

    db.session.add(
        Contact(
            full_name=data["name"],
            email=data["email"],
            phone=data["contact_number"],
            purpose=data["purpose"],
            message=data["message"],
        )
    )
    db.session.commit()

    flash("Message sent successfully", "contact_success")
    return redirect(url_for("contact"))


@app.get("/donations")
def donations():
    return render_template("donations.html", page_content=get_page_content("donations"), file_js="")


@app.get("/programs")
def programs():
    return render_template(
        "programs.html",
        page_content=get_page_content("programs"),
        file_js=f'<script src="{url_for("static", filename="myJS/programs.js")}"></script>',
    )


if __name__ == "__main__":
    app.run(debug=True)
