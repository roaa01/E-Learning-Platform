from typing import List, Dict, Any
from bson import ObjectId
from database.seed import get_database
from database.course_service import CourseService

class AdminService:
    def __init__(self):
        self.db = get_database()
        self.users = self.db.get_collection("users")
        self.course_service = CourseService()

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Fetch all users from the database"""
        # Convert _id to string for UI compatibility
        users = []
        for u in self.users.find({}):
            u_dict = dict(u)
            if "_id" in u_dict:
                u_dict["id"] = str(u_dict["_id"])
            users.append(u_dict)
        return users

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID"""
        try:
            # Try ObjectId first
            res = self.users.delete_one({"_id": ObjectId(user_id)})
            if res.deleted_count > 0:
                return True
        except Exception:
            pass
        
        # Fallback to string id
       # res = self.users.delete_one({"id": user_id})
       # return res.deleted_count > 0

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Get all courses (delegated)"""
        return self.course_service.get_all_courses()

    def delete_course(self, course_id: str) -> bool:
        """Delete any course (delegated)"""
        return self.course_service.delete_course(course_id)
