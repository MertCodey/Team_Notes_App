# Team Notes API

A Flask REST API for a multi-user, cutesy notes app with JWT authentication, PostgreSQL, and Docker support.

## Features

- User registration, login, logout, and refresh (JWT)
- Create, view, and delete notes (user-specific)
- Tagging system for notes
- All notes are public, but only owners can create/delete their own notes
- PostgreSQL database (Dockerized)
- CORS enabled for frontend integration

## Local Development

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- (Recommended) [pipenv](https://pipenv.pypa.io/) or `python -m venv .venv`

### Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/team-notes-api.git
   cd team-notes-api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL with Docker Compose:**
   ```bash
   docker compose up -d db
   ```

5. **Set up your `.env` file:**
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/team_notes
   FLASK_APP=app:create_app
   FLASK_ENV=development
   ```

6. **Run first migrations:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. **Run the app:**
   ```bash
   flask run
   ```
   Or with Gunicorn (production):
   ```bash
   gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
   ```

## Docker (Full App)

To build and run the API in Docker:
```bash
docker build -t team-notes-api .
docker run --env-file .env -p 5000:5000 team-notes-api
```

## API Endpoints

- `POST /register` — Register a new user
- `POST /login` — Login and get JWT tokens
- `POST /logout` — Logout (JWT blocklist)
- `POST /refresh` — Refresh JWT
- `GET /notes` — List all notes
- `POST /notes` — Create a note (JWT required)
- `DELETE /notes` — Delete a note (JWT required, owner only)
- `GET /tags` — List all tags
- `POST /tags` — Create a tag

## Migrations

- `flask db init` — Initialize migrations (run once)
- `flask db migrate -m "message"` — Generate migration
- `flask db upgrade` — Apply migrations

## Deployment

- Build and push Docker image to your registry
- Deploy to GCP Cloud Run, App Engine, or GKE
- Set environment variables in your cloud console

---

**Happy hacking!**