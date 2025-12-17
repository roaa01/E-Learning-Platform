# models.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class UserRole(Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

@dataclass
class User:
    id: Optional[str]
    name: str
    email: str
    role: str
    full_name: Optional[str] = None
    password_hash: Optional[str] = None



    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "fullName": self.full_name,
            "passwordHash": self.password_hash
        }

    def log_out(self) -> None:
        """Log out user by clearing ID"""
        self.id = None

@dataclass
class Student(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "student", full_name, password_hash)

    def request_enrollment(self, course_id: str):
        """Create enrollment request data (use EnrollmentService to persist)"""
        return {
            "studentId": ObjectId(self.id),
            "courseId": course_id,  # Keep as string to match course.id field
            "status": "pending",
            "requestedAt": datetime.now()
        }

    def get_enrolled_courses_data(self):
        """Get query data for enrolled courses (use EnrollmentService to fetch)"""
        return {"studentId": self.id, "status": "approved"}

@dataclass
class Instructor(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "instructor", full_name, password_hash)
    
    # Note: Database operations moved to InstructorService
    # Use InstructorService.get_created_courses(instructor) instead
    # Use EnrollmentService.approve_enrollment(enrollment_id) instead

@dataclass
class Admin(User):
    def __init__(self, **kwargs):
        kwargs['role'] = 'admin'
        # Filter kwargs to match User fields if needed, or assume correct input
        # User is a dataclass, so __init__ accepts args. 
        # But we must be careful: User's generated init expects positional 'id', 'name', 'email', 'role' first?
        # No, dataclass init is: __init__(self, id: Union[str, NoneType], name: str, email: str, role: str, full_name: Union[str, NoneType] = None, password_hash: Union[str, NoneType] = None)
        # So passing **kwargs works if they match these names.
        super().__init__(**kwargs)
