from bson import ObjectId
from datetime import datetime

class InstructorService:
    def __init__(self, courses_col, enrollments_col):
        self.courses = courses_col
        self.enrollments = enrollments_col

    def get_created_courses(self, instructor):
        """Get all courses created by an instructor"""
        try:
            courses_cursor = self.courses.find({"instructorId": instructor.id}, {"title": 1})
            return [{"id": str(c["_id"]), "title": c["title"]} for c in courses_cursor]
        except Exception as e:
            print(f"Error getting instructor courses: {e}")
            return []
    
    # Note: For enrollment approval, use EnrollmentService.approve_enrollment() instead
    # This ensures consistent enrollment management across the application
