
from functools import wraps
from typing import Callable, Any
from .tokens import TokenService
from app.backend.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    RevokedTokenError,
)
from inspect import signature
from ..user import UserManager
from app.backend.db.managers.base import BaseManager
from ....config import AppConfig

class DbAccessLayer:
    """
    Policy enforcement layer that intercepts DB manager calls and validates access.
    
    Usage:
        db = DbAccessLayer(UserManager(), TokenService())
        db.get_work(user_id, token, ...)  # Auto-validates token/scope
    """

    def reload(self,config:AppConfig=None):
        """
        Reloads the database manager and token service with a new configuration.

        Args:
            config (AppConfig, optional): Configuration object to setup the services.
                                          If None, the method returns immediately without changes.
        """
        if not config:
            return
        self._db.setup(config) 
        self._token_service.setup(config) 
    
    def __init__(self, db_manager:UserManager, token_service: TokenService):
        self._db = db_manager
        self._token_service = token_service
        self._wrapped_cache = {}

    def __getattribute__(self, name: str) -> Any:
        # Bypass for internal attributes
        if name in ('_db', '_token_service', '_wrapped_cache', '__class__'):
            return super().__getattribute__(name)
            
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass
            
        # Get the original DB method
        db_method = getattr(self._db, name)

        if not callable(db_method) or name.startswith('__') or name in ['add_user' ,'verify_credentials']:
            return db_method
            
        # Cache wrapped methods
        if name not in self._wrapped_cache:
            self._wrapped_cache[name] = self._create_protected_method(db_method, name)
            
        return self._wrapped_cache[name]

    def _create_protected_method(self, method: Callable, method_name: str) -> Callable:
        
        required_scope = self._map_method_to_scope(method_name)
        
        @wraps(method)
        def wrapped(*args, **kwargs):
          
            if args:
                raise TypeError(
                    f"{method.__name__} only accepts keyword arguments"
                )
            
            try:
                # user_id = kwargs['user_id']
                token = kwargs['token']
            except KeyError as e:
                raise TypeError(
                    f"Missing required argument: {e.args[0]}"
                ) from e

            try:
                token_record = TokenService.validate(
                    raw_token=token,
                    required_scope=required_scope,
                    force_reload=True
                )
                user_id = token_record.user_id
                if 'user_id' not in kwargs:
                  kwargs['user_id']=user_id
                       
            except (InvalidTokenError, ExpiredTokenError, RevokedTokenError) as e:
                self._log_denied_access(method_name, f"Access denied to {method.__name__}: {str(e)}")
                raise

            method_params = signature(method).parameters
            filtered_kwargs = {
                k: v for k, v in kwargs.items() 
                if k in method_params
            }

            return method(**filtered_kwargs)

            
        return wrapped

    def _map_method_to_scope(self, method_name: str) -> str:
        """Maps method names to required scopes."""
        if method_name.startswith(('get_', 'list_')):
            return 'read'
        elif method_name.startswith(('delete_', 'remove_')):
            return 'read_write'
        return 'write'

    def _log_denied_access(self, method: str, error:str):
        """Standardized access denial logging."""
     
        self._token_service._logger.info(f"Access denied to {method}: {error}")

    @property
    def raw_access(self):
        """Bypass property for internal services."""
        return self._db

