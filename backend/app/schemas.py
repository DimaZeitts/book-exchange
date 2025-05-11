from marshmallow import Schema, fields

class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    description = fields.Str()
    owner_id = fields.Int(required=True)
    is_available = fields.Bool()