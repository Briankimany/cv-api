
from .user import UserManager
from .education import EducationManager
from .user_optional import UserOptionalManager
from .work import WorkManager
from .access_manager import DbAccessLayer ,TokenService,TokenIssuer
from ...config import AppConfig ,CONFIG

def init_db_access_layer(config:AppConfig=CONFIG) ->DbAccessLayer:
        """
        Initialize and return a database access layer instance.

        Args:
            config (AppConfig, optional): Configuration object for database and token services.
                                          Defaults to the global CONFIG.

        Returns:
            DbAccessLayer: An instance of DbAccessLayer initialized with UserManager and TokenService.
        """
        return DbAccessLayer(
            db_manager=UserManager(config=config),  
            token_service=TokenService(config=config) 
        )


__all__ = [
    'DbAccessLayer',
    'UserManager',
    'EducationManager',
    'UserOptionalManager',
    'WorkManager',
    'init_db_access_layer',
    'TokenIssuer'
]
