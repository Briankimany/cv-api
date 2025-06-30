from typing import Dict

from app.backend.models import User ,Education,WorkExperience,UserOptionalData
from .work import WorkManager ,Session
from .education import EducationManager
from .user_optional import UserOptionalManager

from app.backend.exceptions import (
    InvalidDataError,
    UserNotFoundError,
    DuplicateEmailError,
    AuthenticationError
)
from werkzeug.security import generate_password_hash,check_password_hash
from app.backend.config import AppConfig ,CONFIG

class UserManager(WorkManager, EducationManager, UserOptionalManager):
    """
    Central manager for all user-related operations including:
    - Core user CRUD
    - Authentication
    - Integrated access to work/education/optional data
    # """
    def __init__(self, config : AppConfig=CONFIG):
        """

        Args:
            config (AppConfig, optional): config object . Defaults to CONFIG.
        """
        super().__init__(config)
     
    @classmethod
    def add_user(cls, user_data: Dict) -> Dict:
        """
        Creates a new user account with password hashing.
        
        Args:
            user_data: Must contain 'email', 'password', and 'first_name'
            
        Returns:
            Created user instance 
            
        Raises:
            InvalidDataError: If required fields are missing
            DuplicateEmailError: If email already exists
        """
        required = ['email', 'password', 'first_name']
        missing = [field for field in required if field not in user_data]
        if missing:
            raise InvalidDataError(f"Missing required fields: {', '.join(missing)}")

        with cls.writer_session() as session:
           
            if session.query(User).filter_by(email=user_data['email']).first():
                raise DuplicateEmailError(f"Email {user_data['email']} already registered")

            new_user = User(
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                second_name=user_data.get('second_name'),
                phone=user_data.get('phone')
            )
            session.add(new_user)
            session.flush()
            
            cls._logger.info(f"Created new user: {user_data['email']}")
            return new_user.to_dict()

    @classmethod
    def get_user(cls, user_id: int) -> User:
        """
        Retrieves user profile by ID (without sensitive data).
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            User profile instance
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        session:Session = cls.reader

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
            
        return user
    

    @classmethod
    def get_user_by_email(cls, email: str) -> User:
        """
        Retrieves user profile by email (without sensitive data).
        
        Args:
            email: The email to search for
            
        Returns:
            User profile instance
            
        Raises:
            UserNotFoundError: If email not found
        """
       
        user = cls.reader.query(User).filter_by(email=email).first()
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user 

    @classmethod
    def update_user(cls, user_id: int, update_data: Dict) -> Dict:
        """
        Updates user profile with partial data.
        Automatically hashes password if provided.
        
        Args:
            user_id: ID of user to update
            update_data: Fields to update
            
        Returns:
            Updated user profile as dictionary
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DuplicateEmailError: If updating to an existing email
        """
        if 'password' in update_data:
            update_data['password'] = generate_password_hash(update_data['password'])

        with cls.writer_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            if 'email' in update_data:
                existing = session.query(User)\
                                .filter_by(email=update_data['email'])\
                                .first()
                if existing and existing.id != user_id:
                    raise DuplicateEmailError(f"Email {update_data['email']} already in use")

            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            cls._logger.info(f"Updated user profile {user_id}")
            return user.to_dict()

    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        """
        Deletes a user account and all associated data.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            True if deletion succeeded, False if user didn't exist
        """
        with cls.writer_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                cls._logger.warning(f"Attempted to delete non-existent user {user_id}")
                return False

            # Delete associated records
            session.query(WorkExperience).filter_by(user_id=user_id).delete()
            session.query(Education).filter_by(user_id=user_id).delete()
            session.query(UserOptionalData).filter_by(user_id=user_id).delete()
            
            # Delete user
            session.delete(user)
            cls._logger.warning(f"Deleted user {user_id} and all associated data")
            return True

    @classmethod
    def verify_credentials(cls, email: str, password: str) -> Dict:
        """
        Authenticates a user by email and password.
        
        Args:
            email: User's email
            password: Plaintext password to verify
            
        Returns:
            User profile if authentication succeeds
            
        Raises:
            AuthenticationError: If credentials are invalid
            UserNotFoundError: If email doesn't exist
        """
        session :Session= cls.reader
        
        user = session.query(User).filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            raise AuthenticationError("Invalid credentials or user not found. ")

        cls._logger.info(f"Successful login for {email}")
        return user.to_dict()
    
  
    @classmethod
    def get_full_profile(cls, user_id: int) -> Dict:
        """
        Retrieves complete user profile with all associated data.
        
        Args:
            user_id: ID of user to retrieve
            
        Returns:
            Dictionary containing:
            - Core profile
            - Work experience
            - Education
            - Optional data (skills/awards/projects)
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        profile = cls.get_user(user_id) 
        
        return {
            **profile,
            'work_experience': cls.get_work(user_id),
            'education': cls.get_education(user_id),
            'skills': cls.get_optional(user_id, 'skill'),
            'awards': cls.get_optional(user_id, 'award'),
            'projects': cls.get_optional(user_id, 'project')
        }
