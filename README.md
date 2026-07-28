# Tweens - Flask App

This project has been migrated to Flask with Jinja templates. The Flask app lives in the flask_app directory and serves static assets from the public folder.

## Requirements

- Python 3.10+
- Node.js 18+

Install dependencies:

```
pip install -r requirements.txt
```

## Configuration

Set these environment variables before running:

- DATABASE_URL: SQLAlchemy connection string for the existing database
- SECRET_KEY: Flask session secret
- ADMIN_NAME: Admin username for the news editor (default: tweenstongogara)
- ADMIN_PASSWORD: Admin password (default: tweens@2020Admin)

Example for local dev:

```
export DATABASE_URL="sqlite:///database.sqlite3"
export SECRET_KEY="change-me"
```

## Run the app

### Option 1: one-command development start

```
make run
```

The first run creates a local `.venv`, installs Python dependencies from `requirements.txt`, and starts Flask on http://127.0.0.1:5000.

If you want to prepare the environment separately:

```
make setup
```

### Option 2: manual Python

```
python flask_app/app.py
```

The server also starts on http://127.0.0.1:5000.

## Database migrations

Apply the site content migration:

```
python flask_app/migrations/0001_site_content.py
```

## Tailwind build

Install Node dependencies:

```
npm install
```

Build Tailwind once:

```
npm run build
```

Or watch during development:

```
npm run watch
```

Alternatively, use the Makefile:

```
make build
```

For development watching:

```
make watch
```

For a clean rebuild:

```
make clean
```

## Notes

- Static assets (CSS, JS, images) are served directly from public.
- Database tables used: updates_table, testimony_table, newsletter_table, contact_table, site_content_table.
- Admin editor is available at /news/createValidate.
