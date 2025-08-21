from db import db

class TagModel(db.Model):
    __tablename__ = "tags"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    notes = db.relationship("NoteModel", secondary="notes_to_tags", back_populates="tags")

    