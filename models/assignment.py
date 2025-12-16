from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from bson import ObjectId

@dataclass
class Assignments:
    id: Optional[str] = None
    courseId: str = ""
    title: str = ""
    description: str = ""
    dueDate: Optional[datetime] = None
    submissionType: str = "text"
    maxGrade: float = 100.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "courseId": self.courseId,
            "title": self.title,
            "description": self.description,
            "dueDate": self.dueDate,
            "submissionType": self.submissionType,
            "maxGrade": self.maxGrade,
            "created_at": self.created_at
        }

@dataclass
class Submission:
    id: Optional[str] = None
    assignmentId: str = ""
    studentId: str = ""
    content: str = ""
    submittedDate: datetime = field(default_factory=datetime.utcnow)
    grade: Optional[float] = None
    feedback: Optional[str] = None
    contentType: str = "text"
    status: str = "submitted" # Helper field

    def to_dict(self):
        return {
            "assignmentId": ObjectId(self.assignmentId),
            "studentId": ObjectId(self.studentId),
            "content": self.content,
            "submittedDate": self.submittedDate,
            "grade": self.grade,
            "feedback": self.feedback,
            "contentType": self.contentType,
            "status": self.status
        }
