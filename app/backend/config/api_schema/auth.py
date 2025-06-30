
from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Valid email address required"
        }
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "Password is required",
            "validator_failed": "Password must be at least 8 characters"
        }
    )

class RegistrationSchema(Schema):
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            "required": "First name is required",
            "invalid": "1-50 characters allowed"
        }
    )
    second_name = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        error_messages={
            "invalid": "Max 50 characters allowed"
        }
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Valid email address required"
        }
    )
    phone = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s-]{6,15}$'),
        error_messages={
            "invalid": "Valid phone number required (6-15 digits)"
        }
    )
    # password = fields.Str(
    #     required=True,
    #     validate=[
    #         validate.Length(min=8),
    #         validate.Regexp(
    #             r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    #             error="Password must contain uppercase, lowercase, number and special char"
    #         )
    #     ],
    #     error_messages={
    #         "required": "Password is required"
    #     }
    # )
    password = fields.Str(
        required=True,
        error_messages={
            "required": "Password is required"
        }
    )


class TokenIssueSchema(Schema):
    level = fields.Str(
        required=True,
        validate=validate.OneOf(["read", "write", "read_write"]),
        error_messages={
            "required": "Token level is required",
            "validator_failed": "Must be one of: read, write, read_write"
        }
    )
    description = fields.Str(
        required=False,
        allow_none=True,
        validate=[
            validate.Length(max=100)
        ],
        error_messages={
            "invalid": "Description must be a string under 100 characters",
            "validator_failed": "Description must be a string under 100 characters",
        }
    )


class TokenListSchema(Schema):
    pass


class TokenRevokeByCredentialsSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class TokenRevokeByTokenSchema(Schema):
    master_token = fields.Str(required=True)
    child_token = fields.Str(required=True)


class TokenRevokeSchema(Schema):
    def load(self, data, *args, **kwargs):
        if 'email' in data:
            return TokenRevokeByCredentialsSchema().load(data)
        else:
            return TokenRevokeByTokenSchema().load(data)