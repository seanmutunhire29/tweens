from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import markdown
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_
from markupsafe import Markup, escape
from werkzeug.utils import secure_filename

try:
    from flask_app.db_migrations import run_migrations
    from flask_app.models import (
        Admins, Achievement, Activity, Contact, HeroSlide, Newsletter,
        Program, ProgramMedia, SiteContent, Testimony, Updates, db,
    )
except ImportError:
    from db_migrations import run_migrations
    from models import (
        Admins, Achievement, Activity, Contact, HeroSlide, Newsletter,
        Program, ProgramMedia, SiteContent, Testimony, Updates, db,
    )

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


def current_admin_user() -> Admins | None:
    uid = session.get("admin_user_id")
    if uid:
        return Admins.query.get(uid)
    return None


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


DEFAULT_ACHIEVEMENTS = [
    {"title": "Empowering Students", "image": "images/achieveEmpower.png", "text": "In a remarkable display of leadership and mentorship, we inspired more than seven girls to retake their O-Level national exams after they initially faced setbacks. Recognizing the challenges these girls were experiencing, we took the initiative to provide emotional and academic support, encouraging them to overcome their doubts and persevere in their educational journey."},
    {"title": "Impactful Outreach", "image": "images/achieveOutreach.jpeg", "text": "Through dedicated efforts, we reached more than 500 students via awareness campaigns and motivational sessions aimed at fostering personal growth and academic success."},
    {"title": "Comprehensive Student Support", "image": "images/achieveStudentSupport.png", "text": "We provided a wide range of essential services to up to 200 students, ensuring they had the resources and support necessary for academic success and personal growth."},
    {"title": "Scholarship Success", "image": "images/achieveScholarSuccess.jpeg", "text": "We celebrated an incredible milestone as five of our students earned full scholarships for their A-Level studies at the prestigious USAP Community School, run by Education Matters."},
    {"title": "International Scholarships", "image": "images/achieveInternationalScholarships.png", "text": "A total of eight of our dedicated members have earned scholarships to pursue higher education abroad, marking a significant achievement in their academic journeys."},
    {"title": "O-Level Success", "image": "images/achieveOLevelSuccess.png", "text": "Tens of non-formal education students successfully passed their O-Level exams, a direct result of the dedicated tutoring provided by TWEENS tutors."},
    {"title": "Night Study Solar Lights", "image": "images/achieveSolarLights.png", "text": "Thanks to the solar lights facilitated through TWEENS by Naledi, more than 50 girls now have the ability to study at night in their homes, overcoming the barriers of limited electricity access."},
    {"title": "Book Donation", "image": "images/achieveBookDonation.png", "text": "Through the generous donation of more than 200 books by Kate Chambers, the JRS local library has received a significant boost in its collection."},
    {"title": "Church Outreach Initiative", "image": "images/achieveChurch.png", "text": "In 2023, we successfully reached out to 1,920 individuals across nine Christian denominations during our church visit initiative."},
]

DEFAULT_PROGRAMS = [
    {"title": "Tutoring lessons", "description": "Our tutoring lessons offer personalized academic support to help students excel in their studies.", "category": "academic", "show_image": "imagePrograms/progTutoringLessons1.jpeg", "media": ["imagePrograms/progTutoringLessons1.jpeg", "imagePrograms/progTutoringLessons2.jpeg", "imagePrograms/progTutoringLessons3.jpeg", "imagePrograms/progTutoringLessons4.jpeg"]},
    {"title": "Study spaces", "description": "Our study spaces provide a quiet and comfortable environment where students can focus, collaborate, and achieve their academic goals.", "category": "academic", "show_image": "imagePrograms/progStudySpaces.png", "media": ["imagePrograms/progStudy1.png"]},
    {"title": "Scholarship mentorship", "description": "We provide guidance and mentorship to help students navigate scholarship opportunities and application processes.", "category": "academic", "show_image": "imagePrograms/progScholarship.png", "media": ["imagePrograms/progScholarshipMentorship1.jpeg", "imagePrograms/progScholarshipMentorship2.jpeg", "imagePrograms/progScholarshipMentorship3.jpeg"]},
    {"title": "Internet Access", "description": "Stay connected and access online resources with our high-speed internet, providing 50GB of data per month.", "category": "resources", "show_image": "imagePrograms/progInternet.png", "media": ["imagePrograms/progInternet.png"]},
    {"title": "Laptops & iPads", "description": "Enhance your learning experience with access to our five laptops and eight iPads.", "category": "resources", "show_image": "images/laptops-ipads_enhanced.jpg", "media": ["images/laptops-ipads_enhanced.jpg"]},
    {"title": "Form 3 & 4 Textbooks", "description": "Access a collection of Form 3 and 4 textbooks covering key subjects to support your studies.", "category": "academic", "show_image": "imagePrograms/progBooks.png", "media": ["imagePrograms/progTextbooks1.jpeg", "imagePrograms/progTextbooks2.jpeg"]},
    {"title": "Motivational sessions", "description": "Stay inspired and driven with our motivational sessions designed to encourage personal growth and academic excellence.", "category": "wellbeing", "show_image": "imagePrograms/progMotivation.png", "media": ["imagePrograms/progMotivation.png"]},
    {"title": "Wide range of books", "description": "Discover a diverse collection of books covering various subjects, including academics, self-improvement, fiction, and career development.", "category": "wellbeing", "show_image": "imagePrograms/progWideRangeOfBooks.jpeg", "media": ["imagePrograms/progWideRangeOfBooks.jpeg"]},
    {"title": "U.S. College Application Books", "description": "Gain valuable insights into the U.S. college application process with our collection of books.", "category": "resources", "show_image": "imagePrograms/progUSColleges.jpeg", "media": ["imagePrograms/progUSColleges.jpeg"]},
    {"title": "Board games", "description": "Take a break and challenge your mind with our engaging board games!", "category": "wellbeing", "show_image": "imagePrograms/progChess.png", "media": ["imagePrograms/progBoard1.jpeg", "imagePrograms/progBoard2.jpeg", "imagePrograms/progBoard3.jpeg", "imagePrograms/progBoard4.jpeg", "imagePrograms/progBoard5.jpeg"]},
]

DEFAULT_ACTIVITIES = [
    {"title": "Big to young sister mentorship", "description": "Older, more experienced students mentoring younger girls, offering academic guidance, emotional support, and motivation to help them succeed in their studies and personal growth.", "image": "images/homeGirlsClub.jpeg"},
    {"title": "Girls book club", "description": "A safe and engaging space where girls come together to read, discuss books, and develop a love for learning while fostering discussions on empowerment and leadership.", "image": "images/homeCleanUp.png"},
    {"title": "Parent Teacher Association", "description": "Parents, teachers, and mentors collaborate to discuss students' academic progress, challenges, and well-being to create a nurturing learning environment.", "image": "images/Parent-Teacher.jpg"},
    {"title": "A level study program", "description": "Academic support, resources, and mentorship for students preparing for A-Level exams, including structured study sessions and guidance on scholarships.", "image": "images/homeALevel.png"},
    {"title": "Education awareness campaigns", "description": "Advocating for the importance of education through motivational talks, workshops, and outreach that inspire learners, parents, and stakeholders.", "image": "images/HomeEducationAwarenessCampains.jpeg"},
    {"title": "Student seminars and workshops", "description": "Interactive learning experiences where students gain academic, career, and personal development skills through expert talks and mentorship.", "image": "images/HomeStudentSeminars.jpeg"},
    {"title": "O-Level tutoring and homework support", "description": "Personalized academic assistance to improve exam performance, build confidence, and strengthen academic skills.", "image": "images/HomeOLevelTutoringAndHomework.JPG"},
    {"title": "Extracurricular offerings", "description": "Opportunities to explore activities beyond academics such as sports, arts, leadership programs, and social clubs.", "image": "images/HomeExtracurricularsAtTweens.jpeg"},
    {"title": "Clean up campaigns", "description": "Promoting environmental awareness and responsibility within the community through cleanup activities and waste management education.", "image": "images/HomeCleanUpCampain.JPG"},
]

DEFAULT_HERO_SLIDES = [
    {"image": "images/home1.png"},
    {"image": "images/home2.jpeg"},
    {"image": "images/home3.png"},
]


def save_uploaded_image(file_obj) -> str | None:
    if not file_obj or not file_obj.filename or not allowed_file(file_obj.filename):
        return None
    filename = f"{int(datetime.utcnow().timestamp())}_{secure_filename(file_obj.filename)}"
    file_obj.save(UPLOAD_DIR / filename)
    return f"updateImages/{filename}"


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


def seed_list_data() -> None:
    if Achievement.query.count() == 0:
        for i, item in enumerate(DEFAULT_ACHIEVEMENTS):
            db.session.add(Achievement(title=item["title"], image=item["image"], text=item["text"], sort_order=i))
        db.session.commit()
    if Program.query.count() == 0:
        for i, item in enumerate(DEFAULT_PROGRAMS):
            prog = Program(title=item["title"], description=item["description"], category=item["category"], show_image=item["show_image"], sort_order=i)
            db.session.add(prog)
            db.session.flush()
            for j, media_path in enumerate(item.get("media", [])):
                db.session.add(ProgramMedia(program_id=prog.id, image=media_path, sort_order=j))
        db.session.commit()
    if Activity.query.count() == 0:
        for i, item in enumerate(DEFAULT_ACTIVITIES):
            db.session.add(Activity(title=item["title"], description=item["description"], image=item["image"], sort_order=i))
        db.session.commit()
    if HeroSlide.query.count() == 0:
        for i, item in enumerate(DEFAULT_HERO_SLIDES):
            db.session.add(HeroSlide(image=item["image"], sort_order=i))
        db.session.commit()


def seed_root_user() -> None:
    """Ensure a root admin exists (credentials from env vars)."""
    root_name, root_pw = admin_credentials()
    existing = Admins.query.filter_by(username=root_name).first()
    if not existing:
        root = Admins(username=root_name, is_root=True, password="")
        root.set_password(root_pw)
        db.session.add(root)
        db.session.commit()
    elif not existing.password_hash:
        # Migrate legacy row: set hash + root flag
        existing.set_password(root_pw)
        existing.is_root = True
        db.session.commit()


with app.app_context():
    run_migrations()
    db.create_all()
    seed_site_content()
    seed_list_data()
    seed_root_user()


@app.context_processor
def inject_global_site_content():
    global_content = get_page_content("global")
    return {
        "global_content": global_content.get("branding", {}),
        "footer_content": global_content.get("footer", {}),
        "current_endpoint": request.endpoint,
    }


@app.get("/")
def home():
    updates = public_news_query().order_by(func.coalesce(Updates.published_at, Updates.created_at).desc(), Updates.id.desc()).all()
    activities = Activity.query.order_by(Activity.sort_order).all()
    hero_slides = HeroSlide.query.order_by(HeroSlide.sort_order).all()
    return render_template(
        "home.html",
        updates=updates,
        activities=activities,
        hero_slides=hero_slides,
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
    achievement_list = Achievement.query.order_by(Achievement.sort_order).all()
    program_list = Program.query.order_by(Program.sort_order).all()
    activity_list = Activity.query.order_by(Activity.sort_order).all()
    hero_slides = HeroSlide.query.order_by(HeroSlide.sort_order).all()
    admin_user = current_admin_user()
    admin_users = Admins.query.order_by(Admins.id).all() if (admin_user and admin_user.is_root) else []
    return render_template(
        "add_updates.html",
        authenticated=is_authenticated(),
        current_admin=admin_user,
        admin_users=admin_users,
        news=news,
        contacts=contacts,
        newsletters=newsletters,
        testimonies=testimonies,
        site_content_editor=get_site_content_editor(),
        achievements=achievement_list,
        programs=program_list,
        activities=activity_list,
        hero_slides=hero_slides,
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
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")

    user = Admins.query.filter_by(username=name).first()
    if user and user.check_password(password):
        session["authenticated"] = True
        session["admin_user_id"] = user.id
        return redirect(url_for("news_create_page"))

    session["authenticated"] = False
    session.pop("admin_user_id", None)
    flash("Invalid credentials.", "login_error")
    return redirect(url_for("news_validate_page"))


@app.get("/admin/logout")
def admin_logout():
    session.pop("authenticated", None)
    session.pop("admin_user_id", None)
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
    achievement_list = Achievement.query.order_by(Achievement.sort_order).all()
    return render_template(
        "achievements.html",
        testimonies=testimonies,
        achievements=achievement_list,
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
    program_list = Program.query.order_by(Program.sort_order).all()
    return render_template(
        "programs.html",
        programs=program_list,
        page_content=get_page_content("programs"),
        file_js=f'<script src="{url_for("static", filename="myJS/programs.js")}"></script>',
    )


# =========================================================================
#  ADMIN — ACHIEVEMENTS CRUD
# =========================================================================

@app.post("/admin/achievements/add")
def admin_achievement_add():
    if not is_authenticated():
        abort(403)
    title = request.form.get("title", "").strip()
    text = request.form.get("text", "").strip()
    if not title:
        flash("Achievement title is required.", "content_error")
        return redirect(url_for("news_create_page"))
    img = request.files.get("image")
    image_path = save_uploaded_image(img) or ""
    max_order = db.session.query(func.max(Achievement.sort_order)).scalar() or 0
    db.session.add(Achievement(title=title, image=image_path, text=text, sort_order=max_order + 1))
    db.session.commit()
    flash("Achievement added.", "content_success")
    return redirect(url_for("news_create_page"))


@app.post("/admin/achievements/<int:item_id>/edit")
def admin_achievement_edit(item_id):
    if not is_authenticated():
        abort(403)
    item = Achievement.query.get_or_404(item_id)
    item.title = request.form.get("title", item.title).strip()
    item.text = request.form.get("text", item.text).strip()
    img = request.files.get("image")
    if img and img.filename:
        new_path = save_uploaded_image(img)
        if new_path:
            if item.image.startswith("updateImages/"):
                old = PUBLIC_DIR / item.image
                if old.exists():
                    old.unlink()
            item.image = new_path
    db.session.commit()
    flash("Achievement updated.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/achievements/<int:item_id>/delete")
def admin_achievement_delete(item_id):
    if not is_authenticated():
        abort(403)
    item = Achievement.query.get_or_404(item_id)
    if item.image.startswith("updateImages/"):
        old = PUBLIC_DIR / item.image
        if old.exists():
            old.unlink()
    db.session.delete(item)
    db.session.commit()
    flash("Achievement deleted.", "content_success")
    return redirect(url_for("news_create_page"))


# =========================================================================
#  ADMIN — PROGRAMS CRUD
# =========================================================================

@app.post("/admin/programs/add")
def admin_program_add():
    if not is_authenticated():
        abort(403)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "academic").strip()
    if not title:
        flash("Program title is required.", "content_error")
        return redirect(url_for("news_create_page"))
    show_img = request.files.get("show_image")
    show_path = save_uploaded_image(show_img) or ""
    max_order = db.session.query(func.max(Program.sort_order)).scalar() or 0
    prog = Program(title=title, description=description, category=category, show_image=show_path, sort_order=max_order + 1)
    db.session.add(prog)
    db.session.flush()
    media_files = request.files.getlist("media_images")
    for j, mf in enumerate(media_files):
        if mf and mf.filename:
            mp = save_uploaded_image(mf)
            if mp:
                db.session.add(ProgramMedia(program_id=prog.id, image=mp, sort_order=j))
    db.session.commit()
    flash("Program added.", "content_success")
    return redirect(url_for("news_create_page"))


@app.post("/admin/programs/<int:item_id>/edit")
def admin_program_edit(item_id):
    if not is_authenticated():
        abort(403)
    item = Program.query.get_or_404(item_id)
    item.title = request.form.get("title", item.title).strip()
    item.description = request.form.get("description", item.description).strip()
    item.category = request.form.get("category", item.category).strip()
    show_img = request.files.get("show_image")
    if show_img and show_img.filename:
        new_path = save_uploaded_image(show_img)
        if new_path:
            if item.show_image.startswith("updateImages/"):
                old = PUBLIC_DIR / item.show_image
                if old.exists():
                    old.unlink()
            item.show_image = new_path
    media_files = request.files.getlist("media_images")
    max_media_order = db.session.query(func.max(ProgramMedia.sort_order)).filter_by(program_id=item.id).scalar() or 0
    for j, mf in enumerate(media_files):
        if mf and mf.filename:
            mp = save_uploaded_image(mf)
            if mp:
                db.session.add(ProgramMedia(program_id=item.id, image=mp, sort_order=max_media_order + j + 1))
    db.session.commit()
    flash("Program updated.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/programs/<int:item_id>/delete")
def admin_program_delete(item_id):
    if not is_authenticated():
        abort(403)
    item = Program.query.get_or_404(item_id)
    if item.show_image.startswith("updateImages/"):
        old = PUBLIC_DIR / item.show_image
        if old.exists():
            old.unlink()
    for m in item.media_images:
        if m.image.startswith("updateImages/"):
            old = PUBLIC_DIR / m.image
            if old.exists():
                old.unlink()
    db.session.delete(item)
    db.session.commit()
    flash("Program deleted.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/programs/media/<int:media_id>/delete")
def admin_program_media_delete(media_id):
    if not is_authenticated():
        abort(403)
    m = ProgramMedia.query.get_or_404(media_id)
    if m.image.startswith("updateImages/"):
        old = PUBLIC_DIR / m.image
        if old.exists():
            old.unlink()
    db.session.delete(m)
    db.session.commit()
    flash("Media image removed.", "content_success")
    return redirect(url_for("news_create_page"))


# =========================================================================
#  ADMIN — ACTIVITIES CRUD
# =========================================================================

@app.post("/admin/activities/add")
def admin_activity_add():
    if not is_authenticated():
        abort(403)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title:
        flash("Activity title is required.", "content_error")
        return redirect(url_for("news_create_page"))
    img = request.files.get("image")
    image_path = save_uploaded_image(img) or ""
    max_order = db.session.query(func.max(Activity.sort_order)).scalar() or 0
    db.session.add(Activity(title=title, description=description, image=image_path, sort_order=max_order + 1))
    db.session.commit()
    flash("Activity added.", "content_success")
    return redirect(url_for("news_create_page"))


@app.post("/admin/activities/<int:item_id>/edit")
def admin_activity_edit(item_id):
    if not is_authenticated():
        abort(403)
    item = Activity.query.get_or_404(item_id)
    item.title = request.form.get("title", item.title).strip()
    item.description = request.form.get("description", item.description).strip()
    img = request.files.get("image")
    if img and img.filename:
        new_path = save_uploaded_image(img)
        if new_path:
            if item.image.startswith("updateImages/"):
                old = PUBLIC_DIR / item.image
                if old.exists():
                    old.unlink()
            item.image = new_path
    db.session.commit()
    flash("Activity updated.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/activities/<int:item_id>/delete")
def admin_activity_delete(item_id):
    if not is_authenticated():
        abort(403)
    item = Activity.query.get_or_404(item_id)
    if item.image.startswith("updateImages/"):
        old = PUBLIC_DIR / item.image
        if old.exists():
            old.unlink()
    db.session.delete(item)
    db.session.commit()
    flash("Activity deleted.", "content_success")
    return redirect(url_for("news_create_page"))


# =========================================================================
#  ADMIN — HERO SLIDES CRUD
# =========================================================================

@app.post("/admin/hero-slides/add")
def admin_hero_slide_add():
    if not is_authenticated():
        abort(403)
    img = request.files.get("image")
    image_path = save_uploaded_image(img)
    if not image_path:
        flash("Please upload a valid image.", "content_error")
        return redirect(url_for("news_create_page"))
    max_order = db.session.query(func.max(HeroSlide.sort_order)).scalar() or 0
    db.session.add(HeroSlide(image=image_path, sort_order=max_order + 1))
    db.session.commit()
    flash("Hero slide added.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/hero-slides/<int:item_id>/delete")
def admin_hero_slide_delete(item_id):
    if not is_authenticated():
        abort(403)
    item = HeroSlide.query.get_or_404(item_id)
    if item.image.startswith("updateImages/"):
        old = PUBLIC_DIR / item.image
        if old.exists():
            old.unlink()
    db.session.delete(item)
    db.session.commit()
    flash("Hero slide removed.", "content_success")
    return redirect(url_for("news_create_page"))


# =========================================================================
#  ADMIN — USER MANAGEMENT (root only)
# =========================================================================

@app.post("/admin/users/add")
def admin_user_add():
    admin = current_admin_user()
    if not admin or not admin.is_root:
        abort(403)
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    if not username or not password:
        flash("Username and password are required.", "content_error")
        return redirect(url_for("news_create_page"))
    if Admins.query.filter_by(username=username).first():
        flash("That username already exists.", "content_error")
        return redirect(url_for("news_create_page"))
    new_user = Admins(username=username, is_root=False, password="")
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash(f"User '{username}' created.", "content_success")
    return redirect(url_for("news_create_page"))


@app.get("/admin/users/<int:user_id>/delete")
def admin_user_delete(user_id):
    admin = current_admin_user()
    if not admin or not admin.is_root:
        abort(403)
    target = Admins.query.get_or_404(user_id)
    if target.is_root:
        flash("Cannot delete the root user.", "content_error")
        return redirect(url_for("news_create_page"))
    db.session.delete(target)
    db.session.commit()
    flash(f"User '{target.username}' deleted.", "content_success")
    return redirect(url_for("news_create_page"))


if __name__ == "__main__":
    app.run(debug=True)
