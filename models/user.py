# models.py
from typing import Optional
from datetime import datetime
from patterns.factory import UserFactory
class User:
    def __init__(self, id: Optional[str], name: str, email: str,
                 role: str, full_name: Optional[str] = None,
                 password_hash: Optional[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.full_name = full_name
        self.password_hash = password_hash


    def log_out(self) -> None:
        self.id = None

    def updateProfile(self, full_name: str = None, email: str = None) -> bool:
        if self.id is None:
            return False
        if full_name:
            self.full_name = full_name
        if email:
            self.email = email

class Student(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "student", full_name, password_hash)

    def request_enrollment(self, course_id: str):
        return {
            "student_id": self.id,
            "course_id": course_id,
            "status": "pending",
            "requested_at": datetime.now()
        }

    def get_enrolled_courses_data(self):
        return {"student_id": self.id, "status": "approved"}

        
class Instructor(User):
    def __init__(self, id: Optional[str], name: str, email: str, full_name: Optional[str] = None, password_hash: Optional[str] = None):
        super().__init__(id, name, email, "instructor", full_name, password_hash)
    def get_created_courses(self):
       try:
        courses = self.db.get_collection("courses").find(
            {"instructor_id": self.id},         
            {"title": 1}                        
        )
        return [{"id": str(c["_id"]), "title": c["title"]} for c in courses]
       except Exception as e:
        print("Error getting courses:", e)
        return []
    def approve_enrollment(self,enrollmentId):
        try:
            result = self.db.get_collection("enrollments").update_one(
                {"_id": ObjectId(enrollmentId)},
                {"$set": {"status": "approved", "approved_at": datetime.now()}}
            )
            return result.modified_count == 1
        except Exception as e:
            print("Error approving enrollment:", e)
            return False

class Admin(User):
    
    def __init__(self, **kwargs):
        
        kwargs['role'] = 'admin'
        super().__init__(**kwargs)
    
    def  viewA_allsers(self, role: str = None):
        try:
            if role:
                users = self.db.execute_query(
                    "SELECT * FROM users WHERE role = ?",
                    (role,)
                )
            else:
                users = self.db.execute_query("SELECT * FROM users")
            
            return users
        except:
            return []
    
    def delete_user(self, user_id: int) -> bool:
        try:
            self.db.execute_update(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            return True
        except:
            return False