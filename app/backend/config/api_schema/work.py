
from marshmallow import Schema, fields, EXCLUDE

class WorkCreateSchema(Schema):
    """Schema for creating work experience records."""
    class Meta:
        unknown = EXCLUDE

    organization_name = fields.Str(required=True)
    description = fields.Str(required=True)
    witness = fields.Str(required=True)
    comment = fields.Str(required=False)

class WorkUpdateSchema(Schema):
    """Schema for updating work experience records."""
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(required=True)
    organization_name = fields.Str(required=False)
    description = fields.Str(required=False)
    witness = fields.Str(required=False)
    comment = fields.Str(required=False)

class WorkDeleteSchema(Schema):
    """Schema for deleting work experience records."""
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(required=True)