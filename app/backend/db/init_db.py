
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.backend.models import Base  
from app.backend.config import CONFIG ,AppConfig

def initialize_database(config:AppConfig=None):
    """
    Creates the database and tables if they do not exist.
    
    Args:
        config (AppConfig, optional): Configuration object containing database URL.
                                      Defaults to None, in which case the global CONFIG is used.

    Returns:
        str: The database URL used for the connection.

    Raises:
        SQLAlchemyError: If there is an error during database initialization.
    """
    try:
        config = config or CONFIG
        engine = create_engine(config.database_url)

        inspector = inspect(engine)
        if inspector.get_table_names():
            return CONFIG.database_url

        Base.metadata.create_all(engine)

        return CONFIG.database_url
    except SQLAlchemyError as e:
        print(f"Database initialization failed: {e}")
        raise e 
    