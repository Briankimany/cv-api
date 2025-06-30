from .base_view import *


class EducationView(BaseView):

    
    def __init__(self, config: AppConfig = CONFIG, 
                 expected_data_format: Schema = EducationCreateSchema):
        super().__init__(config, expected_data_format)
 
    def post(self):
        """Add a new education record for the authenticated user."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(EducationCreateSchema)
        user_id = self.token_issuer.get_user_id(token)
        request_data['user_id']=user_id
        new_record = self.db_access.add_education(token=token,data=request_data)
        return self.return_response({
            "msg": "Education record added.",
            **new_record
        })

    def get(self):
        """Get education records for the authenticated user."""
        token = self.extract_token_from_header()
        user_id = self.token_issuer.get_user_id(token)
        
        if 'id' in request.args:
            record = self.db_access.get_education_by_id(user_id=user_id, record_id=int(request.args['id']),token=token)
            return self.return_response([record.to_dict()])
        
        records = self.db_access.get_education(user_id=user_id ,token=token)
        return self.return_response([r.to_dict() for r in records])

    def put(self):
        """Update an existing education record."""
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(EducationUpdateSchema)
        

        updated_record = self.db_access.update_education(
            token=token,
            record_id=request_data['id'],
            update_data=request_data
        )
        return self.return_response({
            "msg": "Education record updated.",
            "education": updated_record
        })

    def delete(self):
        """Delete an education record."""
        token = self.extract_token_from_header()

        request_data = self.parse_and_validate(EducationDeleteSchema)
        
        self.db_access.delete_education(token = token ,record_id=request_data['id'])
        return self.return_response({
            "msg": "Education record deleted."
        })