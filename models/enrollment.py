from datetime import datetime
from typing import Optional, Dict, Any, Union
from bson import ObjectId

class Enrollment:
    def __init__(self, 
                 studentId: Union[int, str], 
                 courseId: Union[int, str], 
                 enrolledDate: Optional[datetime] = None,
                 status: str = "pending",
                 id: Optional[Union[int, str]] = None):
        
        self.id = id
        self.studentId = studentId
        self.courseId = courseId
        self.enrolledDate = enrolledDate or datetime.now()
        self.status = status  # pending, active, completed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "studentId": self.studentId,
            "courseId": self.courseId,
            "enrolledDate": self.enrolledDate,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enrollment':
        """Create Enrollment object from dictionary"""
        return cls(
            id=str(data.get("_id")) if data.get("_id") else data.get("id"),
            studentId=data.get("studentId") or data.get("student_id"), # Support both for compatibility
            courseId=data.get("courseId") or data.get("course_id"),
            enrolledDate=data.get("enrolledDate") or data.get("requested_at"),
            status=data.get("status", "pending")
        )

    def __repr__(self):
        return f"<Enrollment(id={self.id}, studentId={self.studentId}, courseId={self.courseId}, status={self.status})>"
