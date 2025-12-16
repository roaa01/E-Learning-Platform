from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Any
from .seed import get_database
from models.assignment import Assignments, Submission

class AssignmentService:
    def __init__(self):
        self.db = get_database()
        self.assignments = self.db.get_collection("assignments")
        self.submissions = self.db.get_collection("submissions")

    def create_assignment(self, courseId: str, title: str, description: str, dueDate: datetime, submissionType: str, maxGrade: float = 100.0) -> str:
        """Create a new assignment and return its ID"""
        assignment = Assignments(
            course_id=courseId,
            title=title,
            description=description,
            due_date=dueDate,
            submission_type=submissionType,
            max_grade=maxGrade
        )
        
        doc = assignment.to_dict()
        result = self.assignments.insert_one(doc)
        return str(result.inserted_id)

    def get_assignment(self, assignmentId: str) -> Optional[Dict[str, Any]]:
        try:
            return self.assignments.find_one({"_id": ObjectId(assignmentId)})
        except Exception as e:
            print(f"Error getting assignment: {e}")
            return None

    def submit_assignment(self, assignmentId: str, studentId: str, content: str, contentType: str = "text") -> bool:
        doc = {
            "assignmentId": ObjectId(assignmentId),
            "studentId": ObjectId(studentId),
            "content": content,
            "contentType": contentType,
            "status": "submitted",
            "submittedDate": datetime.utcnow(),
            "grade": None,
            "feedback": None
        }
        try:
            # Check if already submitted
            existing = self.submissions.find_one({
                "assignmentId": ObjectId(assignmentId),
                "studentId": ObjectId(studentId)
            })
            if existing:
                # Update existing submission
                self.submissions.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "content": content, 
                        "contentType": contentType,
                        "submittedDate": datetime.utcnow()
                    }}
                )
            else:
                self.submissions.insert_one(doc)
            return True
        except Exception as e:
            print(f"Error submitting assignment: {e}")
            return False

    def grade_submission(self, assignmentId: str, studentId: str, raw_score: float, feedback: str = "") -> float:
        """
        Grade a submission using the Decorator Pattern.
        Apply LatePenaltyDecorator automatically.
        """
        from patterns.grading_decorator import BasicGrader, LatePenaltyDecorator
        # Placeholder for grading logic
        # 1. Fetch Data
        assignment_doc = self.get_assignment(assignmentId)
        if not assignment_doc:
            return 0.0
            
        submission_doc = self.get_submission(assignmentId, studentId)
        if not submission_doc:
            return 0.0

        # Construct Models (partial) for Grading Logic
        # (We only need dates and maxGrade for the strategy)
        from models.assignment import Assignments, Submission
        assignment = Assignments(
            due_date=assignment_doc.get("dueDate"), 
            max_grade=assignment_doc.get("maxGrade", 100.0)
        )
        submission = Submission(
            submitted_date=submission_doc.get("submittedDate")
        )

        # 2. Build Decorator Chain
        grader = BasicGrader()
        grader = LatePenaltyDecorator(grader)
        # You could add more decorators here, e.g. ExtraCreditDecorator

        # 3. Calculate Final Grade
        final_grade = grader.calculate_grade(submission, assignment, raw_score)

        # 4. Save to Database
        self.submissions.update_one(
            {"_id": submission_doc["_id"]},
            {"$set": {
                "grade": final_grade,
                "feedback": feedback,
                "status": "graded"
            }}
        )
        
        return final_grade

    def get_submission(self, assignmentId: str, studentId: str) -> Optional[Dict[str, Any]]:
        try:
            return self.submissions.find_one({
                "assignmentId": ObjectId(assignmentId),
                "studentId": ObjectId(studentId)
            })
        except Exception as e:
            print(f"Error getting submission: {e}")
            return None
    
    def delete_assignment(self, assignmentId: str) -> bool:
        """Delete an assignment and all its submissions"""
        try:
            # Delete the assignment
            result = self.assignments.delete_one({"_id": ObjectId(assignmentId)})
            
            # Delete all submissions for this assignment
            self.submissions.delete_many({"assignmentId": ObjectId(assignmentId)})
            
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting assignment: {e}")
            return False
    
    def get_all_submissions(self, assignmentId: str) -> List[Dict[str, Any]]:
        """Get all submissions for an assignment (for instructor)"""
        try:
             pipeline = [
                {"$match": {"assignmentId": ObjectId(assignmentId)}},
                {"$lookup": {
                    "from": "users",
                    "localField": "studentId",
                    "foreignField": "_id",
                    "as": "student"
                }},
                {"$unwind": "$student"},
                {"$project": {
                    "submission_id": {"$toString": "$_id"},
                    "assignmentId": {"$toString": "$assignmentId"},
                    "studentId": {"$toString": "$studentId"},
                    "student_name": "$student.name",
                    "student_email": "$student.email",
                    "content": 1,
                    "submittedDate": 1,
                    "status": 1,
                    "grade": 1,
                    "contentType": 1
                }}
            ]
             return list(self.submissions.aggregate(pipeline))
        except Exception as e:
            print(f"Error getting submissions: {e}")
            return []
