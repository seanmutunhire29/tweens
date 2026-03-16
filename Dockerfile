# ── Stage 1: build Tailwind CSS ───────────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci 2>/dev/null || npm install

COPY tailwind.config.js ./
COPY src/ ./src/
COPY flask_app/templates/ ./flask_app/templates/
COPY public/css/ ./public/css/

RUN npm run tailwind:build 2>/dev/null || npx tailwindcss \
    -i ./src/tailwind.css \
    -o ./public/css/tailwind.css \
    --minify


# ── Stage 2: production Flask image ──────────────────────────────────────────
FROM python:3.11-slim AS app

# Non-root user for security
RUN addgroup --system tweens && adduser --system --ingroup tweens tweens

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application source
COPY flask_app/ ./flask_app/
COPY public/ ./public/

# Copy compiled CSS from frontend stage
COPY --from=frontend /app/public/css/tailwind.css ./public/css/tailwind.css

# Persistent data directories (SQLite DB + uploaded images)
# These are mounted as volumes at runtime; we just ensure they exist.
RUN mkdir -p /data/updateImages \
    && chown -R tweens:tweens /data

# Symlink the upload directory into public so Flask can serve uploads
RUN ln -sfn /data/updateImages ./public/updateImages \
    && chown -h tweens:tweens ./public/updateImages

# Hand off ownership of the whole app dir
RUN chown -R tweens:tweens /app

USER tweens

# Environment defaults (override at runtime via .env or -e flags)
ENV FLASK_APP=flask_app.app \
    FLASK_ENV=production \
    DATABASE_URL=sqlite:////data/database.sqlite3 \
    SECRET_KEY=change-me-in-production \
    PORT=8000

EXPOSE 8000

# Initialise DB on first start, then launch gunicorn
CMD ["sh", "-c", "\
    python -c 'from flask_app.app import app, db, seed_site_content, seed_list_data, seed_root_user; \
               from flask_app.db_migrations import run_migrations; \
               ctx = app.app_context(); ctx.push(); \
               run_migrations(); db.create_all(); \
               seed_site_content(); seed_list_data(); seed_root_user()' 2>/dev/null || true; \
    exec gunicorn flask_app.app:app \
         --bind 0.0.0.0:${PORT} \
         --workers 2 \
         --threads 2 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
"]
