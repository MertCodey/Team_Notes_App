from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  


class UserRegisterSchema(UserSchema):
   email= fields.Str(required=True)

class PlainNoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class NoteSchema(PlainNoteSchema):
    user_id = fields.Int(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)
    tags = fields.List(fields.Nested(lambda: TagSchema(exclude=("notes",))), dump_only=True)

class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    notes = fields.List(fields.Nested(PlainNoteSchema), dump_only=True)  

