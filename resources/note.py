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

blp = Blueprint("Notes", __name__, description="Operations on notes")

@blp.route("/notes")
class NoteList(MethodView):
    @blp.response(200, NoteSchema(many=True))
    def get(self):
        """Get all notes"""
        return NoteModel.query.all()
    
    @jwt_required()
    @blp.arguments(NoteSchema)
    @blp.response(201, NoteSchema)
    def post(self, note_data):
        """Create a new note for the current user only"""
        user_id = get_jwt_identity()
        note = NoteModel(
            title=note_data["title"],
            content=note_data["content"],
            user_id=user_id
        )
        db.session.add(note)
        db.session.commit()
        return note, 201
        
    @jwt_required()
    @blp.arguments(NoteSchema)
    @blp.response(200, NoteSchema)
    def delete(self, note_data):
        """Delete a note (only if you own it)"""
        user_id = get_jwt_identity()
        note = NoteModel.query.filter_by(id=note_data['id']).first()
        if not note:
            abort(404, message="Note not found")
        if note.user_id != user_id:
            abort(403, message="You can only delete your own notes")
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted"}, 200