
from datetime import datetime,date as DateObj
from typing import Dict, List, Optional

from app.backend.config import DATE_FORMAT
from .base import BaseManager ,Session ,AppConfig,CONFIG
from app.backend.models import UserOptionalData
from app.backend.exceptions import InvalidDataError, InvalidOptionalTypeError, OptionalDataNotFoundError
   

class UserOptionalManager(BaseManager):
    """
    Handles CRUD operations for user's optional data including:
    - Skills
    - Awards
    - Projects
    Implements strict type validation and full session management.
    """
 
    VALID_TYPES = {'skill', 'award', 'project'}
    TYPE_DISPLAY_NAMES = {
        'skill': 'Skill',
        'award': 'Award',
        'project': 'Project'
    }

    def __init__(self, config:AppConfig=CONFIG):
        super().__init__(config)

    @classmethod
    def _validate_type(cls, data_type: str) -> None:
        """Validates that the type is one of the allowed values"""
        if data_type not in cls.VALID_TYPES:
            raise InvalidOptionalTypeError(
                f"Invalid type '{data_type}'. Must be one of: {', '.join(cls.VALID_TYPES)}"
            )

    @classmethod
    def add_optional(cls, data: Dict) -> Dict:
        """
        Creates new optional data record after validation.
        
        Args:
            data: Must contain 'user_id', 'type', and 'title' ,'date'
            
        Returns:
            Created record as dictionary
            
        Raises:
            InvalidDataError: If required fields are missing or the date string does not match the parsing string.
            InvalidOptionalTypeError: If type is invalid
        """

        required = ['user_id', 'type', 'title','date']
        missing = [field for field in required if field not in data]
        if missing:
            raise InvalidDataError(f"Missing required fields: {', '.join(missing)}")

        cls._validate_type(data['type'])

        try:
            date=data['date']
            if not isinstance(date,DateObj):
                date = datetime.strptime(date ,DATE_FORMAT).date()
        except ValueError as e:
            raise InvalidDataError(f"Date string must match the format {DATE_FORMAT}")
        
        with cls.writer_session() as session:
            new_record = UserOptionalData(
                user_id=data['user_id'],
                type=data['type'],
                title=data['title'],
                description=data.get('description'),
                date=date
            )
            session.add(new_record)
            session.flush()

            cls._logger.debug(new_record)
            cls._logger.info(
                f"Added {data['type']} record '{data['title']}' "
                f"for user {data['user_id']}"
            )
            return new_record.to_dict()

    @classmethod
    def get_optional(cls, user_id: int, data_type: Optional[str] = None) -> List[UserOptionalData]:
        """
        Retrieves optional data records with optional type filtering.
        
        Args:
            user_id: Owner user ID
            data_type: Optional type filter ('skill', 'award', 'project')
            
        Returns:
            List of UserOptionalData instances
        """
        if data_type:
            cls._validate_type(data_type)

        session :Session = cls.reader
      
        query = session.query(UserOptionalData).filter_by(user_id=user_id)
        if data_type:
            query = query.filter_by(type=data_type)
        records = query.order_by(UserOptionalData.date.desc()).all()
        return records


    @classmethod
    def get_optional_by_id(cls, user_id: int, record_id: int) -> Optional[UserOptionalData]:
        """
        Retrieves a single optional data record with ownership verification.
        
        Args:
            user_id: Owner user ID
            record_id: Record ID to retrieve
            
        Returns:
            UserOptionalData instance or None if not found
        """
        session:Session = cls.reader
       
        record = session.query(UserOptionalData)\
                        .filter_by(id=record_id, user_id=user_id)\
                        .first()
        if not record:
            cls._logger.debug(f"No optional record {record_id} found for user {user_id}")
            raise OptionalDataNotFoundError(f"No optional record {record_id} found for user {user_id}")
        return record 
     
    @classmethod
    def update_optional(cls, record_id: int, update_data: Dict) -> Dict:
        """
        Updates optional data record with partial data.
        allowed fields are 'title', 'description', 'date', 'type'
        
        Args:
            record_id: ID of record to update
            update_data: Fields to update
            
        Returns:
            Updated record instance
            
        Raises:
            OptionalDataNotFoundError: If record doesn't exist
            InvalidOptionalTypeError: If attempting to set invalid type
            InvalidDataError: If an invalid field is provided
        """
        if 'type' in update_data:
            cls._validate_type(update_data['type'])

        with cls.writer_session() as session:
            record = session.query(UserOptionalData).filter_by(id=record_id).first()
            if not record:
                raise OptionalDataNotFoundError(f"Optional record {record_id} not found")

            for field, value in update_data.items():
                if hasattr(record, field):
                    setattr(record, field, value)
                else:
                    raise InvalidDataError(f"Invalid field {field}. The only allowed fileds are ('title', 'description', 'date', 'type'). ")
                
            record.updated_at = datetime.utcnow()
            cls._logger.info(f"Updated optional record {record_id}")
            return record.to_dict()

    @classmethod
    def delete_optional(cls, record_id: int) -> bool:
        """
        Deletes an optional data record.
        
        Args:
            record_id: ID of record to delete
            
        Returns:
            True if deleted, False if record didn't exist
        """
        with cls.writer_session() as session:
            record = session.query(UserOptionalData).filter_by(id=record_id).first()
            if not record:
                cls._logger.warning(f"Attempted to delete non-existent optional record {record_id}")
                return False

            session.delete(record)
            cls._logger.info(f"Deleted optional record {record_id} (Type: {record.type})")
            return True

    @classmethod
    def get_types(cls) -> Dict[str, str]:
        """
        Returns the valid optional data types with their display names.
        
        Returns:
            Dictionary mapping type codes to display names
        """
        return cls.TYPE_DISPLAY_NAMES

    @classmethod
    def search_by_title(cls, user_id: int, search_term: str) -> List[UserOptionalData]:
        """
        Searches optional data by title (case-insensitive partial match).
        
        Args:
            user_id: Owner user ID
            search_term: Text to search in titles
            
        Returns:
            List of UserOptionalData records.
        """
        session :Session = cls.reader
        
        records = session.query(UserOptionalData)\
                        .filter_by(user_id=user_id)\
                        .filter(UserOptionalData.title.ilike(f"%{search_term}%"))\
                        .all()
        return records
