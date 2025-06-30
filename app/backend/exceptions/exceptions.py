
class BaseAPIError(Exception):
    """Base exception with standardized JSON response format"""
    status_code: int = 500
    description: str = "An unexpected error occurred"

    def __init__(self, message: str = None, description: str = None):
        self.message = message or "Server Error"
        self.description = description or self.description

    def to_response(self) -> dict:
        return {
            "msg": self.message,
            "type": type(self).__name__,
            "description": self.description
        }
    def __repr__(self):
        return f"{self.__class__.__name__}: {self.message}"

class InternalServerError(BaseAPIError):
    """Raised when an internal server error occurs"""
    status_code = 500
    description = "An internal server error occurred. We are working to fix it."


class RecordDuplicationError(BaseAPIError):
    """Raised when a record already exists"""
    status_code = 409
    description = "Record already exists"


# UserManager exceptions
class InvalidDataError(BaseAPIError):
    """Missing/wrong fields in user creation/update"""
    status_code = 400
    description = "Request is missing required fields"

class UserNotFoundError(BaseAPIError):
    """User not found in database"""
    status_code = 400
    description = "No user exists with the specified ID"

class DuplicateEmailError(BaseAPIError):
    """Email already exists during registration"""
    status_code = 409
    description = "This email is already registered"

class AuthenticationError(BaseAPIError):
    """Invalid login credentials"""
    status_code = 401
    description = "Incorrect email or password"


# WorkManager exceptions
class WorkRecordNotFoundError(BaseAPIError):
    """Work experience record not found"""
    status_code = 404
    description = "No work record exists with the specified ID"


# EducationManager exceptions
class EducationLevelError(BaseAPIError):
    """Invalid education level (not 1-5)"""
    status_code = 400
    description = "Education level must be between 1 (Primary) and 5 (PhD)"

class EducationRecordNotFoundError(BaseAPIError):
    """Education record not found"""
    status_code = 404
    description = "No education record exists with the specified ID"


# UserOptionalManager exceptions
class InvalidOptionalTypeError(BaseAPIError):
    """Invalid type (not skill/award/project)"""
    status_code = 400
    description = "Type must be one of: skill, award, project"

class OptionalDataNotFoundError(BaseAPIError):
    """Optional data record not found"""
    status_code = 404
    description = "No record exists with the specified ID"