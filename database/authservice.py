import bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from patterns.factory import UserFactory
from models.user import User
class AuthService:
    def __init__(self, user_collection):
        self.users = user_collection
    def sign_up(self, role, name, email, password):
        # Normalize role to lowercase for the factory and DB

             #Build user object (factory) and DB document
            user = UserFactory.create_user(
                role,
                id=None, # database 
                name=name,
                email=email,
                password_hash=None, # database
            )

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user.password_hash = password_hash

            # Build document with role-specific fields
            data = {
                "name": name,
                "email": email,
                "passwordHash": password_hash,
                "role": role,
            }

            # Add role-specific fields to the document
            if role == "instructor":
                data["coursesTeaching"] = []
            elif role == "student":
                data["enrolledCourses"] = []
            data["createdAt"] = datetime.now()

        #check if email registered before
            try:
                result = self.users.insert_one(data)
                user.id = str(result.inserted_id)
                return user
            except DuplicateKeyError:
                # Email already exists
                return None
    def log_in(self, email, password):
        user_doc = self.users.find_one({
            "$or": [
                {"email": email},
            ]
        })

        if not user_doc:
            return None

        if not bcrypt.checkpw(password.encode(), user_doc["passwordHash"].encode()):
            return None

        # Create correct User object using factory
        name_value = user_doc.get("email")
        return UserFactory.create_user(
            user_doc["role"],
            id=str(user_doc["_id"]),
            name=name_value,
            email=user_doc.get("email"),
            password_hash=user_doc.get("passwordHash")
        )
    def get_user_by_id(self, user_id):
        """Get user by ID and return User object"""
        temp = None
        
        try:
            # Try ObjectId first
            temp = self.users.find_one({"_id": ObjectId(user_id)})
        except (TypeError, ValueError):
            # If not a valid ObjectId, try as string
            temp = self.users.find_one({"_id": user_id})
        
        if not temp:
            # Fallback for seeded string IDs
            temp = self.users.find_one({"id": user_id})
        
        if not temp:
            return None
        
        # Return User object for consistency
        name_value = temp.get("email")
        return UserFactory.create_user(
            temp["role"],
            id=str(temp["_id"]),
            name=name_value,
            email=temp.get("email"),
            password_hash=temp.get("passwordHash")
        )
    def authorize(self, user: User, action: str) -> bool:
        """
        Check if the user is authorized to perform the given action.
        """
        #access control
        if not user or not user.role:
            return False
            
        try:
             # Ensure we have an Enum
            if isinstance(user.role, str):
                from models.user import UserRole
                role_enum = UserRole(user.role.strip().lower())
            else:
                role_enum = user.role
        except ValueError:
            return False
        
        from models.user import UserRole

        # 1 Admin
        if role_enum == UserRole.ADMIN:
            return True
            
        # 2 Instructor 
        if role_enum == UserRole.INSTRUCTOR:
            if action in [
                "create_course", 
                "edit_course", 
                "delete_course", 
                "view_submissions", 
                "grade_submission",
                "approve_enrollment",
                "view_my_courses"
            ]:
                return True
            return False

        # 3 Student 
        if role_enum == UserRole.STUDENT:
            if action in [
                "enroll_course", 
                "view_course_content", 
                "submit_assignment",
                "view_my_courses"
            ]:
                return True
            return False

        # Default 
        return False
