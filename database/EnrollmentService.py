from bson import ObjectId
from datetime import datetime

class EnrollmentService:
    def __init__(self, enrollments_col, courses_col):
        self.enrollments = enrollments_col
        self.courses = courses_col

    def enroll_student(self, student, course_id: str):
        print(f"Enrolling student {student.id} in course {course_id}")
        
        # Courses use a custom 'id' field (string), not MongoDB's _id
        course = self.courses.find_one({"id": course_id})
        if not course:
            print(f"Course not found: {course_id}")
            return False
            
        existing = self.enrollments.find_one({
            "studentId": ObjectId(student.id),
            "courseId": course_id  # Store as string to match course.id
        })
        if existing:
            print(f"Enrollment already exists: {existing}")
            return False
            
        enrollment_doc = student.request_enrollment(course_id)
        # Ensure studentId is ObjectId, courseId stays as string
        enrollment_doc["studentId"] = ObjectId(enrollment_doc["studentId"])
        # courseId is already a string from request_enrollment - keep it that way
        
        print(f"Inserting enrollment: {enrollment_doc}")
        try:
            result = self.enrollments.insert_one(enrollment_doc)
            print(f"Enrollment inserted with ID: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"Failed to insert enrollment: {e}")
            return False

    def get_enrolled_courses(self, student):
        query = student.get_enrolled_courses_data()  # {"studentId": "123", "status": "approved"}
        
        try:
            s_oid = ObjectId(query["studentId"])
        except (TypeError, ValueError) as e:
            print(f"Invalid student ID: {e}")
            return []

        pipeline = [
            {"$match": {"studentId": s_oid, "status": query["status"]}},
            {"$lookup": {
                "from": "courses",
                "localField": "courseId",
                "foreignField": "id",  # Match on custom 'id' field, not '_id'
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$project": {"_id": 0, "courseId": 1, "title": "$course.title", "description": "$course.description", "category": "$course.categoryId"}}
        ]
        return list(self.enrollments.aggregate(pipeline))

    def get_pending_enrollments(self, course_id: str):
        """Get pending enrollments for a specific course"""
        # courseId is stored as string to match course.id field
        pipeline = [
            {"$match": {"courseId": course_id, "status": "pending"}},
            {"$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$project": {
                "enrollment_id": {"$toString": "$_id"},
                "student_name": "$student.name",
                "student_email": "$student.email",
                "requestedAt": 1
            }}
        ]
        return list(self.enrollments.aggregate(pipeline))

    def approve_enrollment(self, enrollment_id: str):
        """Approve a student enrollment"""
        print(f"Approving enrollment: {enrollment_id}")
        try:
            result = self.enrollments.update_one(
                {"_id": ObjectId(enrollment_id)},
                {"$set": {"status": "approved", "approvedAt": datetime.now()}}
            )
            print(f"Update result - matched: {result.matched_count}, modified: {result.modified_count}")
            return result.modified_count == 1
        except Exception as e:
            print(f"Error approving enrollment: {e}")
            return False

    def reject_enrollment(self, enrollment_id: str):
        """Reject a student enrollment"""
        try:
            result = self.enrollments.update_one(
                {"_id": ObjectId(enrollment_id)},
                {"$set": {"status": "rejected", "rejectedAt": datetime.now()}}
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"Error rejecting enrollment: {e}")
            return False
    
    def get_enrollment_by_id(self, enrollment_id: str):
        """Get enrollment by ID"""
        try:
            return self.enrollments.find_one({"_id": ObjectId(enrollment_id)})
        except Exception as e:
            print(f"Error getting enrollment: {e}")
            return None
    
    def delete_enrollment(self, enrollment_id: str) -> bool:
        """Delete an enrollment"""
        try:
            result = self.enrollments.delete_one({"_id": ObjectId(enrollment_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting enrollment: {e}")
            return False
    
    def update_enrollment_status(self, enrollment_id: str, status: str) -> bool:
        """Update enrollment status (generic method)"""
        if status not in ["pending", "approved", "rejected"]:
            print(f"Invalid status: {status}")
            return False
        
        try:
            update_data = {"status": status}
            if status == "approved":
                update_data["approvedAt"] = datetime.now()
            elif status == "rejected":
                update_data["rejectedAt"] = datetime.now()
            
            result = self.enrollments.update_one(
                {"_id": ObjectId(enrollment_id)},
                {"$set": update_data}
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"Error updating enrollment status: {e}")
            return False