from bson import ObjectId
from datetime import datetime

class EnrollmentService:
    def __init__(self, enrollments_col, courses_col):
        self.enrollments = enrollments_col
        self.courses = courses_col

    def enroll_student(self, student, course_id: str):
        print(f"[DEBUG] Enrolling student {student.id} in course {course_id}")
        
        # Courses use a custom 'id' field (string), not MongoDB's _id
        course = self.courses.find_one({"id": course_id})
        if not course:
            print(f"[DEBUG] Course not found: {course_id}")
            return False
            
        existing = self.enrollments.find_one({
            "student_id": ObjectId(student.id),
            "course_id": course_id  # Store as string to match course.id
        })
        if existing:
            print(f"[DEBUG] Enrollment already exists: {existing}")
            return False
            
        enrollment_doc = student.request_enrollment(course_id)
        # Ensure student_id is ObjectId, course_id stays as string
        enrollment_doc["student_id"] = ObjectId(enrollment_doc["student_id"])
        # course_id is already a string from request_enrollment - keep it that way
        
        print(f"[DEBUG] Inserting enrollment: {enrollment_doc}")
        try:
            result = self.enrollments.insert_one(enrollment_doc)
            print(f"[DEBUG] Enrollment inserted with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"[DEBUG] Failed to insert enrollment: {e}")
            return False

    def get_enrolled_courses(self, student):
        query = student.get_enrolled_courses_data()  # {"student_id": "123", "status": "approved"}
        
        try:
            s_oid = ObjectId(query["student_id"])
        except:
            return []

        pipeline = [
            {"$match": {"student_id": s_oid, "status": query["status"]}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "id",  # Match on custom 'id' field, not '_id'
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$project": {"_id": 0, "course_id": 1, "title": "$course.title", "description": "$course.description", "category": "$course.category"}}
        ]
        return list(self.enrollments.aggregate(pipeline))

    def get_pending_enrollments(self, course_id: str):
        """Get pending enrollments for a specific course"""
        # course_id is stored as string to match course.id field
        pipeline = [
            {"$match": {"course_id": course_id, "status": "pending"}},
            {"$lookup": {
                "from": "users",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$project": {
                "enrollment_id": {"$toString": "$_id"},
                "student_name": "$student.name",
                "student_email": "$student.email",
                "requested_at": 1
            }}
        ]
        return list(self.enrollments.aggregate(pipeline))

    def approve_enrollment(self, enrollment_id: str):
        """Approve a student enrollment"""
        print(f"[DEBUG] Approving enrollment: {enrollment_id}")
        try:
            result = self.enrollments.update_one(
                {"_id": ObjectId(enrollment_id)},
                {"$set": {"status": "approved", "approved_at": datetime.now()}}
            )
            print(f"[DEBUG] Update result - matched: {result.matched_count}, modified: {result.modified_count}")
            return result.modified_count == 1
        except Exception as e:
            print(f"Error approving enrollment: {e}")
            return False

    def reject_enrollment(self, enrollment_id: str):
        """Reject a student enrollment"""
        try:
            result = self.enrollments.update_one(
                {"_id": ObjectId(enrollment_id)},
                {"$set": {"status": "rejected", "rejected_at": datetime.now()}}
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"Error rejecting enrollment: {e}")
            return False
    