from datetime import datetime
from typing import Optional, Dict, Any, Union
from bson import ObjectId

class Enrollment:
    def __init__(self, 
                 student_id: Union[int, str], 
                 course_id: Union[int, str], 
                 enrolled_date: Optional[datetime] = None,
                 status: str = "pending",
                 id: Optional[Union[int, str]] = None):
        
        self.id = id
        self.student_id = student_id
        self.course_id = course_id
        self.enrolled_date = enrolled_date or datetime.now()
        self.status = status  # pending, approved, rejected

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrolled_date": self.enrolled_date,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enrollment':
        """Create Enrollment object from dictionary"""
        return cls(
            id=str(data.get("_id")) if data.get("_id") else data.get("id"),
            student_id=data.get("student_id") or data.get("studentId"),  # Support both for compatibility
            course_id=data.get("course_id") or data.get("courseId"),
            enrolled_date=data.get("enrolled_date") or data.get("enrolledDate") or data.get("requested_at"),
            status=data.get("status", "pending")
        )
    
    def is_pending(self) -> bool:
        """Check if enrollment is pending approval"""
        return self.status == "pending"
    
    def is_approved(self) -> bool:
        """Check if enrollment is approved"""
        return self.status == "approved"
    
    def is_rejected(self) -> bool:
        """Check if enrollment is rejected"""
        return self.status == "rejected"

 

