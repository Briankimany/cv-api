
from ..base_view import *



class LoginView(BaseView):
    """Handles user login and master token issuance."""
    
    def __init__(self, config:AppConfig=CONFIG, expected_data_format = LoginSchema):
        super().__init__(config, expected_data_format)
     
    def post(self):
        
        credentials = self.parse_and_validate()
        user = self.db_access.verify_credentials(**credentials)

        self.logger.debug(f"User {user['email']} is being logged in")
        token = self.token_issuer.token_service.get_by_user_and_scope(
            user_id=user['id'],
            scope='read_write'
        )
        
        if not token:
            token = self.token_issuer.issue_master_token(
                user_id=user['id'],
                ip=request.remote_addr
            )
        else:
            token = None

        return self.return_response({"token": token, "msg": "Login successful"})