from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.backend.models import AccessToken
from app.backend.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    RevokedTokenError,
    InsufficientScopeError,
    QuotaExceededError,
    RecordDuplicationError
)
from .token_manager import TokenService ,CONFIG ,AppConfig


class TokenIssuer:
    """
    Handles two-tier token issuance system with master/child tokens.
    Integrates with TokenService for core operations while adding issuance policies.
    
    Usage:
        issuer = TokenIssuer()
        master_token = issuer.issue_master_token(user_id=123, ip="192.168.1.1")
        child_token = issuer.issue_child_token(master_token, scope="read", ip="192.168.1.1")
    """
    def __init__(self ,config:AppConfig=CONFIG):
        self.__class__.token_service = TokenService(config=config)
        self.__class__._logger = self.token_service._logger

    @classmethod
    def revoke_master(cls,user_id:int) ->bool:
        """
        Revokes a user's master token.
        
        Args:
            user_id: The user ID whose token is to be revoked.
            
        Returns:
            bool: True if token was successfully revoked, False otherwise.
        """
        cls._logger.debug(f"Revoking master token for user {user_id}")
        token_record = TokenService.get_by_user_and_scope(user_id=user_id,
                                                          scope='read_write',
                                                          revoked=False)
        if not token_record:
            cls._logger.warning(f"Attempt to revoke non-existent master token for user {user_id}")
            return False
        TokenService.revoke(token_record.id)
        TokenService._logger.info(f"Master token for user {user_id} revoked")
        return True
    
    @classmethod
    def issue_master_token(cls, user_id: int, ip: Optional[str] = None,
                           description: Optional[str] = 'MASTER-TOKEN') -> str:
        """
        Issues a master token with read_write scope.
        
        Args:
            user_id: Owner's user ID
            ip: Originating IP address (optional)
            description: A human-readable description of the token.
            
        Returns:
            str: Raw token string
            
        Raises:
            QuotaExceededError: If user exceeds token limit
        """
        cls._logger.debug(f"Issuing master token for user {user_id}")
        try:
            if TokenService.get_by_user_and_scope(user_id=user_id,
                                                  scope='read_write',revoked=False):
                raise RecordDuplicationError("Master token already exists. You need to revoke it before getting a new one.")
            
            token = TokenService.issue(
                user_id=user_id,
                scope="read_write",
                ip=ip,
                description=description 
            )
            cls._logger.info(f"Master token issued for user {user_id}")
            return token
        except (QuotaExceededError,RecordDuplicationError) as e:
            cls._logger.error(f"Error issuing master token for user {user_id}: {str(e)}")
            raise
        except Exception as e:
            cls._logger.critical(f"Unexpected error issuing master token: {str(e)}")
            raise

    @classmethod
    def issue_child_token(cls, master_token: str, scope: str,
                         ip: Optional[str] = None, 
                         description: Optional[str] = None) -> str:
        """
        Issues a child token after validating master token.
        
        Args:
            master_token: Valid read_write master token
            scope: Desired scope ('read' or 'write')
           
            ip: Originating IP (optional)
            description: Human-readable token description (optional)
            
        Returns:
            str: Raw child token
            
        Raises:
            InvalidTokenError: If master token is invalid or there is a user mismatch.
            ExpiredTokenError: If master token expired
            RevokedTokenError: If master token was revoked
            InsufficientScopeError: If scope is invalid
            QuotaExceededError: If token limit reached
        """
        cls._logger.debug(f"Attempting to issue {scope} child token")
        
        try:
            # Validate master token
            token_record = TokenService.validate(master_token, required_scope="read_write")
     
            
            # Issue child token
            child_token = TokenService.issue(
                user_id=token_record.user_id,
                scope=scope,
                ip=ip ,
                description=description,
                parent_token=master_token
            )
            
            cls._logger.debug(
                f"Issued {scope} child token for user {token_record.user_id} "
                f"(parent: {token_record.id})"
            )
            return child_token
            
        except (InvalidTokenError, ExpiredTokenError, RevokedTokenError) as e:
            cls._logger.info(f"Invalid master token: {str(e)}")
            raise
        except InsufficientScopeError as e:
            cls._logger.info(
                f"Scope violation for master token {token_record.id}: {str(e)}"
            )
            raise
        except QuotaExceededError as e:
            cls._logger.info(f"Token quota exceeded: {str(e)}")
            raise
        except Exception as e:
            cls._logger.critical(f"Unexpected error issuing child token: {str(e)}")
            raise

    @classmethod
    def list_user_tokens(cls, master_token: str ,user_id:int=None) -> List[AccessToken]:
        """
        Lists all tokens for a user after validating master token.
        
        Args:
            
            master_token: Valid read_write token
            user_id: Target user ID (optional)
            
        Returns:
            List[AccessToken]: Token records
            
        Raises:
            Same as issue_child_token
        """
       
        
        try:
            # Validate master token and ownership
            token_record = TokenService.validate(master_token, required_scope="read_write")
            if user_id:
                if  not token_record or token_record.user_id != user_id:
                    raise InvalidTokenError("Token/user mismatch")

            user_id = token_record.user_id
            cls._logger.debug(f"Listing tokens for user {user_id}")

            tokens = TokenService.audit_user_tokens(user_id)
            cls._logger.info(f"Returned {len(tokens)} tokens for user {user_id}")
            
            return tokens
            
        except Exception as e:
            cls._logger.error(f"Failed listing tokens: {str(e)}")
            raise

    @classmethod
    def revoke_token(cls, token: str, master_token: str) -> bool:
        """
        Revokes a token after validating master token privileges.
        
        Args:
            token: Token to revoke
            master_token: Valid read_write token
            
        Returns:
            bool: True if revoked
            
        Raises:
            Same as issue_child_token
        """
        cls._logger.debug(f"Attempting to revoke token")
        
        try:
            # Validate master token
            master_record = TokenService.validate(master_token, required_scope="read_write")
            
            # Validate target token
            target_record = TokenService.validate(token)
            
            # Verify ownership
            if target_record.user_id != master_record.user_id:
                raise InvalidTokenError("Cannot revoke another user's token")
                
            result = TokenService.revoke(target_record.id)
            cls._logger.info(
                f"Revoked token {target_record.id} "
                f"(requested by user {master_record.user_id})"
            )
            return result
            
        except Exception as e:
            cls._logger.error(f"Revocation failed: {str(e)}")
            raise
    
    @classmethod
    def get_user_id(cls, token: str) -> int:
        """
        Retrieves the user ID associated with the given token.

        Args:
            token (str): The raw token string to validate and extract user ID from.

        Returns:
            int: The user ID associated with the token.

        Raises:
            InvalidTokenError: If the token is invalid.
            ExpiredTokenError: If the token has expired.
            RevokedTokenError: If the token has been revoked.
        """
        token_record = cls.token_service.validate(raw_token=token, force_reload=True)
        return token_record.user_id
    

