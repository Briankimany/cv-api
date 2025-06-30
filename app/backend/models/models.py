from datetime import datetime 
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey ,Boolean

from sqlalchemy.orm import declarative_base
Base = declarative_base()

class TimeStapmpedBse(Base):

    __abstract__ = True 

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(TimeStapmpedBse):
    """
    Represents a user account in the system.
    Stores core identity information and authentication credentials.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    password = Column(String(100), nullable=False)

    def to_dict(self) -> dict:
        """
        Converts the User object to a dictionary for API responses.
        Excludes sensitive fields like passwords.
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'email': self.email,
            'phone': self.phone,
        }


class Education(TimeStapmpedBse):
    """
    Tracks a user's academic qualifications.
    Supports standardized education levels (e.g., high school, university).
    """
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    entity_level = Column(Integer, nullable=False)
    entity_name = Column(String(100), nullable=False)
    certification = Column(String(100))

    def to_dict(self) -> dict:
        """
        Serializes education record for API output.
        Includes all non-sensitive fields.
        """
        return {
            'id': self.id,
            'entity_level': self.entity_level,
            'entity_name': self.entity_name,
            'certification': self.certification
        }


class WorkExperience(TimeStapmpedBse):
    """
    Records a user's professional employment history.
    Supports optional witness verification and descriptive notes.
    """
    __tablename__ = 'work_experience'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organization_name = Column(String(100), nullable=False)
    description = Column(Text)
    witness = Column(String(100))
    comment = Column(Text)

    def to_dict(self) -> dict:
        """
        Formats work experience data for API consumption.
        Maintains all organizational details.
        """
        return {
            'id': self.id,
            'organization_name': self.organization_name,
            'description': self.description,
            'witness': self.witness,
            'comment': self.comment
        }


class UserOptionalData(TimeStapmpedBse):
    """
    Flexible storage for user-curated content:
    - Skills
    - Awards
    - Personal projects
    Uses type discrimination for categorization.
    """
    __tablename__ = 'user_optional_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(20), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    date = Column(Date)



    def to_dict(self) -> dict:
        """
        Converts flexible optional data to API-friendly format.
        Includes timestamps for change tracking.
        """
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f"UserOptionalData(id={self.id}, user_id={self.user_id}, type={self.type}, title={self.title}, description={self.description}, date={self.date}, created_at={self.created_at}, updated_at={self.updated_at})"


class AccessToken(TimeStapmpedBse):
    """
    Stores API access tokens with security controls and usage tracking.
    Tokens are hashed before storage (like passwords) for security.
    """
    __tablename__ = 'access_tokens'

    id = Column(Integer, primary_key=True ,autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token_hash = Column(String(256), unique=True, nullable=False)  # Argon2/SHA-256 hashed
    scope = Column(String(20), nullable=False)  # 'read', 'write', 'read_write'
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)
    issued_by_ip = Column(String(45)) 
    usage_count = Column(Integer, default=0)
    description = Column(String)
    parent_token= Column(String)

    def to_dict(self) -> dict:
        """
        Serializes token metadata (excluding the actual hash) for audit logs.
        Never exposes the token value itself.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scope': self.scope,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_revoked': self.is_revoked,
            'usage_count': self.usage_count,
            'description':self.description
        }

    def __repr__(self):
        return (f"AccessToken(id={self.id}, user_id={self.user_id}, "
                f"scope={self.scope}, expires_at={self.expires_at}, "
                f"is_revoked={self.is_revoked}, usage_count={self.usage_count})")