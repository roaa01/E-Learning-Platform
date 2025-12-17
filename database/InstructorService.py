
class InstructorService:
    def __init__(self, courses_col, enrollments_col):
        self.courses = courses_col
        self.enrollments = enrollments_col

    def get_created_courses(self, instructor):
        """Get all courses created by an instructor"""
        try:
            all_courses = self.courses.find({"instructorId": instructor.id}, {"title": 1})
            return [{"id": c.get("id") or str(c["_id"]), "title": c["title"]} for c in all_courses]
        except Exception as e:
            print(f"Error getting instructor courses: {e}")
            return []

