from .exceptions import BaseAPIError

class TokenError(BaseAPIError):
    """Base class for all token-related errors"""
    status_code = 401
    description = "Authentication token error"

class InvalidTokenError(TokenError):
    """Raised when token is malformed or not found"""
    status_code = 401
    description = "Invalid or unrecognized token"

    def __init__(self, message: str = "Invalid token", description: str = None):
        super().__init__(message, description)

class ExpiredTokenError(TokenError):
    """Raised when token has expired"""
    status_code = 403
    description = "Token has expired"

    def __init__(self, message: str = "Token expired", description: str = None):
        super().__init__(message, description)

class RevokedTokenError(TokenError):
    """Raised when token was manually revoked"""
    status_code = 403
    description = "Token was revoked"

    def __init__(self, message: str = "Token revoked", description: str = None):
        super().__init__(message, description)

class InsufficientScopeError(TokenError):
    """Raised when token lacks required permissions"""
    status_code = 403
    description = "Insufficient token scope"

    def __init__(self, 
                 message: str = "Insufficient permissions", 
                 description: str = None,
                 required_scope: str = None,
                 actual_scope: str = None):
        if description is None and required_scope and actual_scope:
            description = f"Required: {required_scope}, Actual: {actual_scope}"
        super().__init__(message, description)

class TokenNotFoundError(TokenError):
    """Raised when specific token record doesn't exist"""
    status_code = 404
    description = "Token not found in database"

    def __init__(self, message: str = "Token not found", description: str = None):
        super().__init__(message, description)

class QuotaExceededError(TokenError):
    """Raised when user exceeds token limits"""
    status_code = 429
    description = "Token quota exceeded"

    def __init__(self, 
                 message: str = "Too many active tokens", 
                 description: str = None,
                 max_tokens: int = None):
        if description is None and max_tokens:
            description = f"Maximum allowed tokens: {max_tokens}"
        super().__init__(message, description)


