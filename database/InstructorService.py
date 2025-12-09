class InstructorService:
    def __init__(self, courses_col, enrollments_col):
        self.courses = courses_col
        self.enrollments = enrollments_col

    def get_created_courses(self, instructor: Instructor):
        courses_cursor = self.courses.find({"instructor_id": instructor.id}, {"title": 1})
        return [{"id": str(c["_id"]), "title": c["title"]} for c in courses_cursor]

    def approve_enrollment(self, enrollment_id: str):
        from datetime import datetime
        from bson import ObjectId

        result = self.enrollments.update_one(
            {"_id": ObjectId(enrollment_id)},
            {"$set": {"status": "approved", "approved_at": datetime.now()}}
        )
        return result.modified_count == 1
    
    
