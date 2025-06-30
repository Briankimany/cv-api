
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker ,Session
from contextlib import contextmanager
from app.backend.models import Base

from app.backend.config.config import CONFIG,AppConfig
from app.backend.logger import CustomLogger
from typing import Generator 

class BaseManager:
    """
    Foundation for all database managers. Handles:
    - Engine initialization
    - Session factory creation
    - Write session context management
    - Read session access
    """
    
    @classmethod
    def _set_class_attributes(cls, reader, logger, engine, session_factory):
        cls.reader = reader
        cls._logger = logger
        cls._session_factory = session_factory
        cls._engine = engine

      

    def __init__(self ,config:AppConfig=CONFIG):
        """
        Initialize the BaseManager with database configuration.

        Args:
            config (AppConfig): Configuration object containing database URL and logger settings.
                               Defaults to the global CONFIG.

        Sets up:
            - A custom logger for database operations.
            - SQLAlchemy engine connected to the configured database URL.
            - Session factory for creating new sessions.
            - A persistent read-only session.
        """
  
        self.setup(config)
                
    def setup(self, config: AppConfig):
        """
        Reconfigures this instance and its class-level attributes with a new AppConfig.

        This is useful when switching database connections (e.g., test → dev).

        Args:
            config (AppConfig): The new configuration to load.
        """

        db_attrs = ['_engine', '_session_factory', 'reader', '_logger']
        for attr in db_attrs:
            
            if hasattr(self.__class__, attr):
               
                delattr(self.__class__, attr) 

        logger = CustomLogger(config=config.loggers['database'])
        engine = create_engine(config.database_url)
        session_factory = sessionmaker(bind=engine)
        reader = session_factory()

        logger.debug(f"Using url {config.database_url}")

        return self.__class__._set_class_attributes(
            reader=reader,
            logger=logger,
            session_factory=session_factory,
            engine=engine
        )

    
    @classmethod
    @contextmanager
    def writer_session(cls) ->Generator[Session,None,None]:
        """
        Context manager for write operations with automatic commit/rollback
        """
        session:Session = cls._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            cls._logger.error(f"Database write failed: {str(e)}")
            raise
        finally:
            session.close()
