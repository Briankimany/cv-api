from datetime import datetime
from typing import Dict, List, Optional

from .base import BaseManager ,Session
from app.backend.models import WorkExperience
from app.backend.exceptions import InvalidDataError, WorkRecordNotFoundError


class WorkManager(BaseManager):
    """
    Handles all database operations for work experience records.
    Implements full CRUD with validation, logging, and session management.
    """

    @classmethod
    def add_work(cls, data: Dict) -> Dict:
        """
        Creates a new work experience record after validating required fields.
        
        Args:
            data: Must contain 'user_id' and 'organization_name'
            
        Returns:
            Dictionary representation of the created record
            
        Raises:
            InvalidDataError: If required fields are missing
        """
      
        if not all(k in data for k in ['user_id', 'organization_name']):
            raise InvalidDataError("Missing required fields: user_id or organization_name")
        if len(data['organization_name']) > 100:
            cls._logger.debug(f"Organization name exceeds the maximum length: {data}")
            raise ValueError("organization_name exceeds max length")

        with cls.writer_session() as session:
            new_work = WorkExperience(
                user_id=data['user_id'],
                organization_name=data['organization_name'],
                description=data.get('description'),
                witness=data.get('witness'),
                comment=data.get('comment')
            )
            session.add(new_work)
            session.flush()
            cls._logger.info(
                f"Added work record at {data['organization_name']} "
                f"for user {data['user_id']}"
            )
            return new_work.to_dict()

    @classmethod
    def get_work(cls, user_id: int) -> List[WorkExperience]:
        """
        Retrieves all work experience records for a specific user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of WorkExperience instances 
        """
        session :Session = cls.reader 
       
        records = session.query(WorkExperience)\
                        .filter_by(user_id=user_id)\
                        .order_by(WorkExperience.id.desc())\
                        .all()
        return records
    

    @classmethod
    def get_work_by_id(cls, user_id: int, record_id: int) -> Optional[WorkExperience]:
        """
        Retrieves a specific work record with ownership verification.
        
        Args:
            user_id: The ID of the user (for ownership check)
            record_id: The ID of the work record
            
        Returns:
            WorkExperience instance or None if not found
        """
        session:Session = cls.reader
    
        record = session.query(WorkExperience)\
                        .filter_by(id=record_id, user_id=user_id)\
                        .first()
        if not record:
            cls._logger.debug(f"No work record found with ID {record_id} for user {user_id}")
            raise WorkRecordNotFoundError(f"Work record {record_id} not found for user {user_id}")
        return record

    @classmethod
    def update_work(cls, record_id: int, update_data: Dict) -> Dict:
        """
        Updates a work experience record with partial data.
        
        Args:
            record_id: The ID of the record to update
            update_data: Dictionary of fields to update
            
        Returns:
            Dictionary representation of the updated record
            
        Raises:
            WorkRecordNotFoundError: If record doesn't exist
        """
        with cls.writer_session() as session:
            record = session.query(WorkExperience).filter_by(id=record_id).first()
            if not record:
                raise WorkRecordNotFoundError(f"Work record {record_id} not found")

            for field, value in update_data.items():
                if hasattr(record, field):
                    setattr(record, field, value)

            record.updated_at = datetime.utcnow()
            cls._logger.info(f"Updated work record {record_id}")
            return record.to_dict()

    @classmethod
    def delete_work(cls, record_id: int) -> bool:
        """
        Deletes a work experience record.
        
        Args:
            record_id: The ID of the record to delete
            
        Returns:
            True if deletion was successful, False if record didn't exist
        """
        with cls.writer_session() as session:
            record = session.query(WorkExperience).filter_by(id=record_id).first()
            if not record:
                cls._logger.warning(f"Attempted to delete non-existent work record {record_id}")
                return False

            session.delete(record)
            cls._logger.info(f"Deleted work record {record_id}")
            return True

    @classmethod
    def get_work_by_organization(cls, user_id: int, org_name: str) -> List[WorkExperience]:
        """
        Retrieves work records filtered by organization name (case-insensitive).
        
        Args:
            user_id: The ID of the user
            org_name: Organization name to search for
            
        Returns:
            List of matching work records
        """
        session :Session = cls.reader
      
        records = session.query(WorkExperience)\
                        .filter_by(user_id=user_id)\
                        .filter(WorkExperience.organization_name.ilike(f"%{org_name}%"))\
                        .all()
        return records 
