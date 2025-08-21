from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from schemas import UserRegisterSchema, UserSchema
from models.users import UserModel
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)
from db import db
from models.users import UserModel
from blocklist import BLOCKLIST  
from models.notes import NoteModel
from models.tags import TagModel
from datetime import datetime
from models.notes_to_tags import notes_to_tags
from schemas import NoteSchema
from schemas import TagSchema


blp = Blueprint("Tags", __name__, description="Operations on tags")

@blp.route("/tags")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        """Get all tags"""
        return TagModel.query.all()
    
    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data):
        """Create a new tag"""
        tag = TagModel(**tag_data)
        db.session.add(tag)
        db.session.commit()
        return tag, 201
