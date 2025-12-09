class EnrollmentService:
    def __init__(self, enrollments_col, courses_col):
        self.enrollments = enrollments_col
        self.courses = courses_col

    def enroll_student(self, student: Student, course_id: str):
        course = self.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            return False
        existing = self.enrollments.find_one({
            "student_id": ObjectId(student.id),
            "course_id": ObjectId(course_id)
        })
        if existing:
            return False
        self.enrollments.insert_one(student.request_enrollment(course_id))
        return True
    def get_enrolled_courses(self, student: Student):
        query = student.get_enrolled_courses_data()  # {"student_id": "123", "status": "approved"}

        pipeline = [
            {"$match": {"student_id": ObjectId(query["student_id"]), "status": query["status"]}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$project": {"_id": 0, "course_id": 1, "title": "$course.title", "description": "$course.description"}}
        ]
        return list(self.enrollments.aggregate(pipeline))
    