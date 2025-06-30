
from datetime import datetime, timedelta ,timezone
from typing import Optional, List
from .token_storage import TokenStorage ,AppConfig,CONFIG
from app.backend.models import AccessToken
import secrets
from app.backend.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    RevokedTokenError,
    InsufficientScopeError,
    TokenNotFoundError,
    QuotaExceededError
)
from app.backend.config import SCOPE_HIERARCHY ,DEFAULT_EXPIRY_DAYS,MAX_TOKENS_PER_USER

class TokenService(TokenStorage):
    """Orchestrates token lifecycle and validation workflows.
    
    Provides business logic for token operations while leveraging TokenStorage
    for low-level database interactions.
    """
    def __init__(self, config:AppConfig = CONFIG):
        super().__init__(config)

    @classmethod
    def issue(cls, user_id: int, scope: str,
               ip: str,description:Optional[str]=None,
               parent_token:Optional[str]=None) -> str:
        """Generates and stores a new access token.
        
        Args:
            user_id: Owner's user ID.
            scope: Permission level ('read', 'write', 'read_write').
            ip: Originating IP address for audit.
            description: A human-readable description of the token.
            parent_token: The master token used to generate new child tokens. 
                If None, the token is a master token.
            
        Returns:
            str: The raw (unhashed) token string (only returned once).
            
        Raises:
            QuotaExceededError: If user exceeds MAX_TOKENS_PER_USER.
        """
        # Check token quota
        active_tokens = cls.reader.query(AccessToken).filter_by(
            user_id=user_id,
            is_revoked=False
        ).count()
        if active_tokens >= MAX_TOKENS_PER_USER:
            raise QuotaExceededError(f"Max tokens ({MAX_TOKENS_PER_USER}) exceeded")

        # Generate token
        raw_token = cls._generate_secure_token()
        hashed_token = cls.hash_token(raw_token)
        if scope.lower() not in SCOPE_HIERARCHY or not scope.strip():
            raise InsufficientScopeError("Scope cannot be empty and must be a valid scope")
        
        # Store token
        token_data = {
            'user_id': user_id,
            'token_hash': hashed_token,
            'scope': scope,
            'expires_at': datetime.now(tz=timezone.utc)+ timedelta(days=DEFAULT_EXPIRY_DAYS),
            'issued_by_ip': ip,
            'description':description,
            'parent_token':parent_token
        }
        
        cls.insert(token_data)
        cls._logger.info(f"Issued {scope} token for user {user_id}")
        return raw_token

    @classmethod
    def validate(cls, raw_token: str, required_scope: Optional[str] = None ,
                 force_reload=False) -> AccessToken:
        """Validates a token against all security requirements.
        
        Args:
            raw_token: The token string to validate.
            required_scope: Minimum scope needed (None skips scope check).
            force_reload :Whether the value should be reloaded from the database.
            
        Returns:
            AccessToken: The validated token record.
            
        Raises:
            InvalidTokenError: If token doesn't exist.
            ExpiredTokenError: If token is expired.
            RevokedTokenError: If token was manually revoked.
            InsufficientScopeError: If scope requirements aren't met.
        """
        hashed_token = cls.hash_token(raw_token)
        if force_reload:
            token = cls.reader.query(AccessToken
                        ).filter(AccessToken.token_hash==hashed_token
                        ).execution_options(populate_existing=True).first()
        else:
            token = cls.get_by_hash(hashed_token)
        
        if not token:
            cls._logger.warning(f"Invalid token attempt: {raw_token[:8]}...")
            raise InvalidTokenError("Invalid token")
            
        if token.expires_at < datetime.utcnow():
            raise ExpiredTokenError("Token expired")
            
        if token.is_revoked:
            raise RevokedTokenError("Token revoked")
            
        if required_scope and not cls._scope_satisfies(token.scope, required_scope):
            raise InsufficientScopeError(
                f"Required: {required_scope}, Actual: {token.scope}"
            )
        
        with cls.writer_session () as session:
            tkn = session.query(AccessToken).filter_by(id=token.id).first()
            tkn.last_used_at = datetime.utcnow()
            tkn.usage_count +=1
           
        token = cls.reader.query(AccessToken).filter_by(id=token.id).execution_options(populate_existing=True).first()

        return token

    @classmethod
    def revoke(cls, token_id: int) -> bool:
        """Revokes a single token by ID.
        
        Args:
            token_id: The token to revoke.
            
        Returns:
            bool: True if revoked, False if already revoked.
            
        Raises:
            TokenNotFoundError: If token doesn't exist.
        """
        if not cls.update_field(token_id, 'is_revoked', True):
            raise TokenNotFoundError(f"Token {token_id} not found")
            
        cls._logger.info(f"Revoked token {token_id}")
        return True

    @classmethod
    def audit_user_tokens(cls, user_id: int) -> List[AccessToken]:
        """Retrieves metadata for all of a user's tokens.
        
        Args:
            user_id: The user to audit.
            
        Returns:
            List[AccessToken]: Token records.
        """
        tokens = cls.reader.query(AccessToken).filter_by(user_id=user_id).all()
        return tokens

    @classmethod
    def _generate_secure_token(cls) -> str:
        """Generates a cryptographically secure random token."""
        
        return secrets.token_urlsafe(64)

    @classmethod
    def _scope_satisfies(cls, actual: str, required: str) -> bool:
        """Checks if token scope meets requirements."""
        return SCOPE_HIERARCHY.get(actual, 0) >= SCOPE_HIERARCHY.get(required, 0)