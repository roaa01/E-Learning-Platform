from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from bson import ObjectId

@dataclass
class Assignments:
    id: Optional[str] = None
    course_id: str = ""
    title: str = ""
    description: str = ""
    due_date: Optional[datetime] = None
    submission_type: str = "text"
    max_grade: float = 100.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for MongoDB (using camelCase for DB consistency)"""
        return {
            "courseId": self.course_id,
            "title": self.title,
            "description": self.description,
            "dueDate": self.due_date,
            "submissionType": self.submission_type,
            "maxGrade": self.max_grade,
            "created_at": self.created_at
        }
    
    def is_late(self, submission_date: datetime) -> bool:
        """Check if a submission date is past the due date"""
        if not self.due_date:
            return False
        return submission_date > self.due_date

@dataclass
class Submission:
    id: Optional[str] = None
    assignment_id: str = ""
    student_id: str = ""
    content: str = ""
    submitted_date: datetime = field(default_factory=datetime.utcnow)
    grade: Optional[float] = None
    feedback: Optional[str] = None
    content_type: str = "text"
    status: str = "submitted" # Helper field

    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            "assignmentId": ObjectId(self.assignment_id),
            "studentId": ObjectId(self.student_id),
            "content": self.content,
            "submittedDate": self.submitted_date,
            "grade": self.grade,
            "feedback": self.feedback,
            "contentType": self.content_type,
            "status": self.status
        }
    
    def is_graded(self) -> bool:
        """Check if submission is graded"""
        return self.grade is not None

   