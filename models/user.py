# models.py
from typing import Optional
from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, id: Optional[str], name: str, email: str,
                 role: str, full_name: Optional[str] = None,
                 password_hash: Optional[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.full_name = full_name
        self.password_hash = password_hash


    def log_out(self) -> None:
        """Log out user by clearing ID"""
        self.id = None

    def updateProfile(self, full_name: str = None, email: str = None) -> bool:
        """Update user profile (in-memory only, use AuthService to persist)"""
        if self.id is None:
            return False
        if full_name:
            self.full_name = full_name
        if email:
            self.email = email
        return True

class Student(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "student", full_name, password_hash)

    def request_enrollment(self, course_id: str):
        """Create enrollment request data (use EnrollmentService to persist)"""
        return {
            "student_id": ObjectId(self.id),
            "course_id": course_id,  # Keep as string to match course.id field
            "status": "pending",
            "requested_at": datetime.now()
        }

    def get_enrolled_courses_data(self):
        """Get query data for enrolled courses (use EnrollmentService to fetch)"""
        return {"student_id": self.id, "status": "approved"}

        
class Instructor(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "instructor", full_name, password_hash)
    
    # Note: Database operations moved to InstructorService
    # Use InstructorService.get_created_courses(instructor) instead
    # Use EnrollmentService.approve_enrollment(enrollment_id) instead

class Admin(User):
    
    def __init__(self, **kwargs):
        kwargs['role'] = 'admin'
        super().__init__(**kwargs)
    
    # Note: Database operations should be handled by services
    # Admin-specific operations should be in a dedicated AdminService
    # For now, admin can use any service methods directly
