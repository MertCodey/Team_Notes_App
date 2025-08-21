import os
from flask import Flask, render_template
import flask_sqlalchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_smorest import Api
from db import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from blocklist import BLOCKLIST
from resources.note import blp as NoteBlueprint
from resources.user import blp as UserBlueprint
from resources.tag import blp as TagBlueprint

migrate = Migrate()
jwt = JWTManager()


def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    database_url = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url.startswith("postgresql://") and \
            "+psycopg" not in database_url and \
            "+psycopg2" not in database_url:
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.setdefault('API_TITLE', 'Team Notes API')
    app.config.setdefault('API_VERSION', 'v1')
    app.config.setdefault('OPENAPI_VERSION', '3.0.3')
    # Ensure JWT secret is provided via environment in production
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY',
        app.config.get('JWT_SECRET_KEY', 'dev-only-change-me')
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Ensure models are imported so Alembic detects them
    from models import (
        users as _users,
        notes as _notes,
        tags as _tags,
        notes_to_tags as _notes_to_tags,
    )
    _ = (_users, _notes, _tags, _notes_to_tags)

    api = Api(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has been revoked."}, 401

    @jwt.needs_fresh_token_loader
    def fresh_token_required_callback(jwt_header, jwt_payload):
        return {"message": "Fresh token required."}, 401

    api.register_blueprint(NoteBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(TagBlueprint)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app