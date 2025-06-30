
from marshmallow import Schema, fields, validate


class OptionalCreateSchema(Schema):
    type = fields.Str(
        required=True,
        validate=validate.OneOf(["skill", "award", "project"]),
        error_messages={
            "required": "Type is required",
            "validator_failed": "Type must be one of: skill, award, project"
        }
    )
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            "required": "Title is required",
            "invalid": "Title must be a string between 1 and 100 characters"
        }
    )
    description = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=300),
        error_messages={
            "invalid": "Description must not exceed 300 characters"
        }
    )
    date = fields.Date(
        required=False,
        allow_none=True,
        error_messages={
            "invalid": "Date must be in ISO format (YYYY-MM-DD)"
        }
    )


class OptionalUpdateSchema(Schema):
    id = fields.Int(
        required=True,
        error_messages={"required": "Record ID is required"}
    )
    title = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(
        required=False,
        validate=validate.Length(max=300)
    )
    date = fields.Date(
        required=False,
        allow_none=True
    )


class OptionalDeleteSchema(Schema):
    id = fields.Int(
        required=True,
        error_messages={"required": "Record ID is required"}
    )
