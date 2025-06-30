
from ..base_view import * 


class TokenView(BaseView):
    """
    Handles token issuance, listing, and revocation.
    """
    def __init__(self,config:AppConfig=CONFIG ,expected_data_format:Schema=TokenRevokeSchema):
        super().__init__(config,expected_data_format)
 
    
    def post(self):
        token = self.extract_token_from_header()
        request_data = self.parse_and_validate(TokenIssueSchema)

        new_token = self.token_issuer.issue_child_token(
            master_token=token,
            scope=request_data['level'],
            ip=self.get_request_remote_addr(),
            description=request_data.get('description')
        )

        return self.return_response({"token": new_token})

    def get(self):
        token = self.extract_token_from_header()
       
        tokens = self.token_issuer.list_user_tokens(
            master_token=token
        )

        return self.return_response({"tokens": [t.to_dict() for t in tokens]})

    def delete(self):
        data = self.parse_and_validate()

        if 'email' in data:  
            user = self.db_access.verify_credentials(**data)
            self.token_issuer.revoke_master(user_id=user['id'])

        else:
            self.token_issuer.revoke_token(
                token=data['child_token'],
                master_token=data['master_token']
            )

        return self.return_response({"success": True})
