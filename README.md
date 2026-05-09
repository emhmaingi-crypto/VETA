# VETA Connect

VETA Connect is a Django application built for TVET students, institutions, and partners. It connects learners to opportunities, mentorship, scholarships, and fair dashboards.

## Quick start

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update the values.
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Seed initial content:
   ```bash
   python manage.py seed
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project structure

- `accounts/` — custom user model, registration, login, profile, dashboard
- `opportunities/` — job and internship listings, applications, AI matching
- `services/` — freelance client requests, proposals, and application tracking
- `mentorship/` — mentor search and requests
- `scholarships/` — scholarship listings
- `templates/` — shared templates and base layout
- `static/` — project CSS and JavaScript

## Environment variables

- `SECRET_KEY` — Django secret key
- `DEBUG` — `True` or `False`
- `ALLOWED_HOSTS` — comma-separated hostnames
- `ANTHROPIC_API_KEY` — Anthropic API key for AI opportunity matching
# VETA
