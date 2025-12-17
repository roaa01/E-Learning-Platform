from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Union
from bson import ObjectId

@dataclass
class Enrollment:
    student_id: Union[int, str]
    course_id: Union[int, str]
    enrolled_date: Optional[datetime] = None
    status: str = "pending"
    id: Optional[Union[int, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "studentId": self.student_id,
            "courseId": self.course_id,
            "enrolledDate": self.enrolled_date,
            "status": self.status
        }
    
    def is_pending(self) -> bool:
        """Check if enrollment is pending approval"""
        return self.status == "pending"
    
    def is_approved(self) -> bool:
        """Check if enrollment is approved"""
        return self.status == "approved"
    
    def is_rejected(self) -> bool:
        """Check if enrollment is rejected"""
        return self.status == "rejected"