from .base import BaseManager ,Session ,AppConfig,CONFIG
from app.backend.models import Education
from app.backend.exceptions import InvalidDataError, EducationLevelError ,EducationRecordNotFoundError


class EducationManager(BaseManager):
    """
    Handles all database operations for education records.
    Implements full CRUD with validation and logging.
    """
    VALID_LEVELS = {
        1: "Primary School",
        2: "High School", 
        3: "Undergraduate",
        4: "Master's",
        5: "PhD"
    }

    def __init__(self, config:AppConfig =CONFIG):

        super().__init__(config)

    @classmethod
    def add_education(cls, data: dict) -> dict:
        """
        Creates a new education record after validating:
        - Required fields (user_id, entity_level, entity_name)
        - Valid education level (1-5)
        """
        required_fields = ['user_id', 'entity_level', 'entity_name']
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise InvalidDataError(f"Missing required fields: {', '.join(missing)}")

        if data['entity_level'] not in cls.VALID_LEVELS:
            raise EducationLevelError(
                f"Invalid level {data['entity_level']}. Must be 1-5"
            )

        with cls.writer_session() as session:
            new_edu = Education(
                user_id=data['user_id'],
                entity_level=data['entity_level'],
                entity_name=data['entity_name'],
                certification=data.get('certification')
            )
            session.add(new_edu)
            session.flush()

            cls._logger.info(
                f"Added education record: {data['entity_name']} "
                f"(Level {data['entity_level']}) for user {data['user_id']}"
            )
            return new_edu.to_dict()

    @classmethod
    def get_education(cls, user_id: int) -> list[Education]:
        """
        Returns all education records for a user as a list of education instances.
        """
        session :Session = cls.reader
     
        records = session.query(Education)\
                        .filter_by(user_id=user_id)\
                        .order_by(Education.entity_level.desc())\
                        .all()
        return records


    @classmethod
    def get_education_by_id(cls, user_id: int, record_id: int) -> Education | None:
        """
        Retrieves a single education record with ownership verification.
        Returns None if record doesn't exist or doesn't belong to user.
        """
        session:Session = cls.reader
        record = session.query(Education)\
                           .filter_by(id=record_id, user_id=user_id)\
                           .first()
        if not record:
            raise EducationRecordNotFoundError(f"No matching record found with the id {record_id} for user_id {user_id}")
        return record 

    @classmethod
    def update_education(cls, record_id: int, update_data: dict) -> dict | None:
        """
        Updates education record with validation:
        - Checks record exists
        - Validates education level if provided
        - Applies partial updates
        """
        if 'entity_level' in update_data and update_data['entity_level'] not in cls.VALID_LEVELS:
            raise EducationLevelError(
                f"Invalid level {update_data['entity_level']}. Must be 1-5"
            )

        with cls.writer_session() as session:
            record = session.query(Education).filter_by(id=record_id).first()
            if not record:
                raise EducationRecordNotFoundError(f"No education found matching the id {record_id}")

            for field, value in update_data.items():
                if hasattr(record, field):
                    setattr(record, field, value)

            cls._logger.info(f"Updated education record {record_id}")
            return record.to_dict()

    @classmethod
    def delete_education(cls, record_id: int) -> bool:
        """
        Deletes an education record and returns success status
        """
        with cls.writer_session() as session:
            record = session.query(Education).filter_by(id=record_id).first()
            if not record:
                return False

            session.delete(record)
            cls._logger.warning(f"Deleted education record {record_id}")
            return True

    @classmethod
    def get_education_levels(cls) -> dict:
        """
        Returns the valid education levels mapping
        """
        return cls.VALID_LEVELS