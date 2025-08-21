from db import db
from datetime import datetime

class NoteModel(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("UserModel", back_populates="notes")
    tags = db.relationship("TagModel", secondary="notes_to_tags", back_populates="notes")

