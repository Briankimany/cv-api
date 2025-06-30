

from datetime import datetime
from typing import Optional, Dict, Any
from ...base import BaseManager ,Session
from app.backend.models import AccessToken
from app.backend.exceptions import (
    RecordDuplicationError as DuplicateTokenError,
    InvalidDataError as InvalidFieldError,
    InvalidDataError as InvalidFilterError
)
from app.backend.logger import CustomLogger
from app.backend.config import CONFIG ,AppConfig


class TokenStorage(BaseManager):
    """Handles low-level database operations for access token management.
    
    This class provides atomic operations for token storage and retrieval,
    abstracting away direct database interactions. All methods are classmethods.
    """

    def __init__(self, config:AppConfig = CONFIG):
        super().__init__(config)

    @classmethod
    def hash_token(cls, raw_token: str) -> str:
        """Applies Argon2 hashing to a raw token string.
        
        Args:
            raw_token: The unhashed token string to secure.
            
        Returns:
            str: The hashed token value.
            
        Note:
            Uses workload=3 for balanced security/performance.
        """
        # TODO: Implement actual Argon2 hashing
        return f"argon2_hashed_{raw_token}"

    @classmethod
    def insert(cls, token_data: Dict[str, Any]) -> dict:
        """Stores a new token record in the database.
        
        Args:
            token_data: Dictionary containing:
                - user_id: int
                - token_hash: str
                - scope: str
                - expires_at: datetime
                - issued_by_ip: str (optional)
                
        Returns:
            dict: dict object with the new token metadata.
            
        Raises:
            DuplicateTokenError: If token_hash already exists.
        """
        with cls.writer_session() as session:
            if session.query(AccessToken).filter_by(token_hash=token_data['token_hash']).first():
                cls._logger.warning(f"Duplicate token hash: {token_data['token_hash'][:8]}...")
                raise DuplicateTokenError("Token already exists")
                
            new_token = AccessToken(**token_data)
            session.add(new_token)
            session.flush()
            
            return new_token.to_dict()

    @classmethod
    def get_by_hash(cls, hashed_token: str) -> Optional[AccessToken]:
        """Retrieves a token record by its hashed value.
        
        Args:
            hashed_token: The Argon2-hashed token string.
            
        Returns:
            Optional[AccessToken]: The token record if found, else None.
        """
        return cls.reader.query(AccessToken).filter_by(token_hash=hashed_token).first()

    @classmethod
    def update_field(cls, token_id: int, field: str, value: Any) -> bool:
        """Atomically updates a single field on a token record.
        
        Args:
            token_id: The ID of the token to update.
            field: The field name to modify.
            value: The new value to set.
            
        Returns:
            bool: True if update succeeded, False if no record was found.
            
        Raises:
            InvalidFieldError: If field doesn't exist on AccessToken model.
        """
        if not hasattr(AccessToken, field):
            raise InvalidFieldError(f"Invalid field: {field}")
            
        with cls.writer_session() as session:
            updated = session.query(AccessToken).filter_by(id=token_id).update(
                {field: value, 'updated_at': datetime.utcnow()}
            )
            return updated > 0

    @classmethod
    def bulk_revoke(cls, filters: Dict[str, Any]) -> int:
        """Revokes multiple tokens matching filter criteria.
        
        Args:
            filters: Dictionary of filter conditions (e.g., {"user_id": "abc"}).
            
        Returns:
            int: Number of tokens revoked.
            
        Raises:
            InvalidFilterError: If filter contains invalid fields.
        """
        invalid_fields = [f for f in filters if not hasattr(AccessToken, f)]
        if invalid_fields:
            raise InvalidFilterError(f"Invalid filter fields: {invalid_fields}")
            
        with cls.writer_session() as session:
            return session.query(AccessToken).filter_by(is_revoked=False).filter_by(**filters).update(
                {'is_revoked': True, 'updated_at': datetime.utcnow()},
                synchronize_session=False
            )

    @classmethod
    def delete_expired(cls) -> int:
        """Permanently removes expired tokens from the database.
        
        Returns:
            int: Number of tokens deleted.
        """
        with cls.writer_session() as session:
            return session.query(AccessToken).filter(
                AccessToken.expires_at < datetime.utcnow()
            ).delete(synchronize_session=False)
        
    @classmethod
    def get_by_user_and_scope(cls ,user_id:int ,scope:str ,revoked:bool=False)->AccessToken:

        """Retrieve a user token based on scope(read ,read_write,write) 
        user_id: The user id
        scope: The scope of the token
        revoked: Whether the token is revoked or not
        Returns:
            AccessToken: The token object

        """
        session:Session = cls.reader
        return session.query(AccessToken
                             ).filter_by(
                                 user_id=user_id, scope=scope, is_revoked=revoked).first()