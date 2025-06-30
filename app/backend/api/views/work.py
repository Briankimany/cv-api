from .base_view import *

class WorkView(BaseView):
    """
    View for managing work experience records via token-authenticated routes.
    Inherits from BaseView to enforce token checks and structured request/response handling.
    """

    def __init__(self, config: AppConfig = CONFIG, 
                 expected_data_format: Schema = WorkCreateSchema):
        super().__init__(config, expected_data_format)

    def post(self):
        """Add a new work experience record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(WorkCreateSchema)
        user_id = self.token_issuer.get_user_id(token)

        request_data['user_id'] = user_id
        record = self.db_access.add_work(
            token=token,
            data=request_data
        )
        return self.return_response({
            "msg": "Work experience added.",
            **record
        })

    def get(self):
        """Get one or all work experience records."""
        token = self.extract_token_from_header()
        user_id = self.token_issuer.get_user_id(token)

        record_id = request.args.get("id")
        if record_id:
            record = self.db_access.get_work_by_id(
                user_id=user_id,
                record_id=int(record_id),
                token=token
            )
            return self.return_response([record.to_dict()])

        records = self.db_access.get_work(
            user_id=user_id,
            token=token
        )
        return self.return_response([r.to_dict() for r in records])

    def put(self):
        """Update a work experience record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(WorkUpdateSchema)
        user_id = self.token_issuer.get_user_id(token)

        self.db_access.update_work(
            user_id=user_id,
            record_id=request_data["id"],
            update_data=request_data,
            token=token
        )
        return self.return_response({
            "msg": "Work record updated."
        })

    def delete(self):
        """Delete a work experience record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(WorkDeleteSchema)
        user_id = self.token_issuer.get_user_id(token)

        self.db_access.delete_work(
            user_id=user_id,
            record_id=request_data["id"],
            token=token
        )
        return self.return_response({
            "msg": "Work record deleted."
        })
