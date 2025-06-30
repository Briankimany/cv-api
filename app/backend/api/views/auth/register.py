
from ..base_view import *



class RegisterView(BaseView):
    """Handles user registration only."""
    def __init__(self,config:AppConfig=CONFIG,excepected_data_format:dict=RegistrationSchema):
        super().__init__(config=config,expected_data_format=excepected_data_format)
    
    
    def post(self):
        user_data = request.get_json()
        user_data = self.parse_and_validate()

        self.logger.info(f"User {user_data['email']} is being registered")
        result = self.db_access.add_user(user_data=user_data)
        
        return self.return_response({"msg": "Registration successful", "user": result})



