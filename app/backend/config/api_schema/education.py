
from marshmallow import Schema, fields, validate, EXCLUDE

class EducationCreateSchema(Schema):
    """
    Schema for creating new education records.
    Matches exactly with the documented requirements.
    """
    class Meta:
        unknown = EXCLUDE 

    entity_level = fields.Int(
        required=True,
        validate=validate.OneOf([1, 2, 3, 4, 5]), 
        error_messages={
            "required": "Education level is required",
            "invalid": "Education level must be 1-5"
        }
    )
    entity_name = fields.Str(
        required=True,
        error_messages={"required": "Institution name is required"}
    )
    certification = fields.Str(required=False) 

  

class EducationUpdateSchema(Schema):
    """
    Schema for updating education records.
    Matches exactly with the documented partial update requirements.
    """
    class Meta:
        unknown = EXCLUDE 

    id = fields.Int(required=True) 
    entity_level = fields.Int(
        required=False,
        validate=validate.OneOf([1, 2, 3, 4, 5]),
        error_messages={"invalid": "Education level must be 1-5"}
    )
    entity_name = fields.Str(required=False)
    certification = fields.Str(required=False)

class EducationDeleteSchema(Schema):
    """
    Simple schema for deleting education records.
    Matches the exact format shown in routes.md.
    """
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(required=True)