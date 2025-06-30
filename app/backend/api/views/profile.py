from .base_view import *

class ProfileView(BaseView):
    """
    Returns the authenticated user's profile details.
    Route: /profile [GET]
    """

    def get(self):
        """Return authenticated user's profile information."""
        token = self.extract_token_from_header()
        user_id = self.token_issuer.get_user_id(token)

        user = self.db_access.get_user(user_id=user_id, token=token)
        
        return self.return_response(user.to_dict())
