
from .base_view import *


class OptionalView(BaseView):
    """
    View for managing optional user content (skills, awards, projects).
    Inherits from BaseView to enforce token checks and structured request/response handling.
    """

    def __init__(self, config: AppConfig = CONFIG, 
                 expected_data_format: Schema = OptionalCreateSchema):
        super().__init__(config, expected_data_format)

    def post(self):
        """Add a new optional record (skill, award, or project)."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(OptionalCreateSchema)
        user_id = self.token_issuer.get_user_id(token)

        request_data["user_id"] = user_id
        record = self.db_access.add_optional(
            user_id=user_id,
            token=token,
            data=request_data
        )

        return self.return_response({
            "msg": "Record added.",
            **record
        })

    def get(self):
        """Get optional records, filtered by type or ID if provided."""
        token = self.extract_token_from_header()
        user_id = self.token_issuer.get_user_id(token)

        record_id = request.args.get("id")
        if record_id:
            record = self.db_access.get_optional_by_id(
                user_id=user_id,
                record_id=int(record_id),
                token=token
            )
            return self.return_response([record.to_dict()])

        data_type = request.args.get("type")
        records = self.db_access.get_optional(
            user_id=user_id,
            token=token,
            data_type=data_type
        )
        return self.return_response([r.to_dict() for r in records])

    def put(self):
        """Update an optional record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(OptionalUpdateSchema)
        user_id = self.token_issuer.get_user_id(token)

        self.db_access.update_optional(
            user_id=user_id,
            record_id=request_data["id"],
            update_data=request_data,
            token=token
        )
        return self.return_response({
            "msg": "Record updated."
        })

    def delete(self):
        """Delete an optional record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(OptionalDeleteSchema)
        user_id = self.token_issuer.get_user_id(token)

        self.db_access.delete_optional(
            user_id=user_id,
            record_id=request_data["id"],
            token=token
        )
        return self.return_response({
            "msg": "Record deleted."
        })
