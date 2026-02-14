from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from models import Contact, Newsletter, Testimony, Updates, db

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


@app.get("/")
def home():
    updates = Updates.query.order_by(Updates.id.desc()).all()
    return render_template(
        "home.html",
        updates=updates,
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
    )


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
    caption = request.form.get("caption", "").strip()
    detail = request.form.get("detail", "").strip()
    image = request.files.get("image")
    errors = {}

    if not title:
        errors["title"] = "Title is required."
    if not caption:
        errors["caption"] = "Caption is required."
    if not detail:
        errors["detail"] = "Detail is required."
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
            errors=errors,
        )

    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
    image_path = f"updateImages/{filename}"
    image.save(UPLOAD_DIR / filename)

    update = Updates(
        title=title,
        detail=detail,
        caption=caption,
        image=image_path,
    )
    db.session.add(update)
    db.session.commit()

    session["authenticated"] = False
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
            errors=errors,
        )

    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
    image_path = f"updateImages/{filename}"
    image.save(UPLOAD_DIR / filename)

    db.session.add(Testimony(name=name, image=image_path, caption=testimony))
    db.session.commit()

    session["authenticated"] = False
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
    caption = request.form.get("caption", "").strip()
    detail = request.form.get("detail", "").strip()
    image = request.files.get("image")

    errors = {}
    if not title:
        errors["title"] = "Title is required."
    if not caption:
        errors["caption"] = "Caption is required."
    if not detail:
        errors["detail"] = "Detail is required."
    if image and not allowed_file(image.filename):
        errors["image"] = "Image must be jpg, jpeg, png, or gif."

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
    update.caption = caption
    update.detail = detail
    db.session.commit()

    session["authenticated"] = False
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
    update = Updates.query.get_or_404(update_id)
    min_id = db.session.query(db.func.min(Updates.id)).scalar()
    max_id = db.session.query(db.func.max(Updates.id)).scalar()
    return render_template(
        "news.html",
        update=update,
        min_id=min_id,
        max_id=max_id,
        file_js="",
    )


@app.get("/about")
def about():
    return render_template(
        "about.html",
        file_js=f'<script src="{url_for("static", filename="myJS/about.js")}"></script>',
    )


@app.get("/achievements")
def achievements():
    testimonies = Testimony.query.order_by(Testimony.id.desc()).all()
    return render_template(
        "achievements.html",
        testimonies=testimonies,
        file_js=f'<script src="{url_for("static", filename="myJS/achievements.js")}"></script>',
    )


@app.get("/contact")
def contact():
    return render_template(
        "contact.html",
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
    return render_template("donations.html", file_js="")


@app.get("/programs")
def programs():
    return render_template(
        "programs.html",
        file_js=f'<script src="{url_for("static", filename="myJS/programs.js")}"></script>',
    )


if __name__ == "__main__":
    app.run(debug=True)
