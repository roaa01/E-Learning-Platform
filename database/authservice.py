import bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from patterns.factory import UserFactory
from models.user import User
class AuthService:
    def __init__(self, user_collection):
        self.users = user_collection
    def sign_up(self, role, name, email, password, full_name=None):
        # Normalize role to lowercase for the factory and DB
        try:
            role_norm = (role or "").strip().lower()

            # Build user object (factory) and DB document
            user = UserFactory.create_user(
                role_norm,
                id=None,
                name=name,
                email=email,
                password_hash=None,
            )

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user.password_hash = password_hash

            # Build document with role-specific fields
            data = {
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "role": role_norm,
            }

            # Add role-specific fields to the document
            if role_norm == "instructor":
                data["courses_teaching"] = []
            elif role_norm == "student":
                data["enrolled_courses"] = []
            data["created_at"] = datetime.now()


            try:
                result = self.users.insert_one(data)
                user.id = str(result.inserted_id)
                return user
            except DuplicateKeyError:
                # Email already exists
                return None
        except Exception as e:
            # Unexpected error (factory mismatch, validation, etc.)
            print(f"sign_up error: {e}")
            return None
    def log_in(self, email_or_name, password):
        user_doc = self.users.find_one({
            "$or": [
                {"email": email_or_name},
                {"name": email_or_name}
            ]
        })

        if not user_doc:
            return None

        if not bcrypt.checkpw(password.encode(), user_doc["password_hash"].encode()):
            return None

        # Create correct User object using factory
        name_value = user_doc.get("name") or user_doc.get("email")
        return UserFactory.create_user(
            user_doc["role"],
            id=str(user_doc["_id"]),
            name=name_value,
            email=user_doc.get("email"),
            full_name=user_doc.get("full_name"),
            password_hash=user_doc.get("password_hash")
        )
    def update_profile(self, user: User, full_name=None, email=None):
        if user.id is None:
            return False
        update_fields = {}
        if full_name: 
            update_fields["full_name"] = full_name
        if email: 
            update_fields["email"] = email
        if not update_fields:
            return False
        try:
            self.users.update_one({"_id": ObjectId(user.id)}, {"$set": update_fields})
            user.updateProfile(full_name, email)  # update object
            return True
        except DuplicateKeyError:
            return False

    def get_user_by_id(self, user_id):
        """Get user by ID and return User object"""
        doc = None
        
        try:
            # Try ObjectId first
            doc = self.users.find_one({"_id": ObjectId(user_id)})
        except (TypeError, ValueError):
            # If not a valid ObjectId, try as string
            doc = self.users.find_one({"_id": user_id})
        
        if not doc:
            # Fallback for seeded string IDs
            doc = self.users.find_one({"id": user_id})
        
        if not doc:
            return None
        
        # Return User object for consistency
        name_value = doc.get("name") or doc.get("email")
        return UserFactory.create_user(
            doc["role"],
            id=str(doc["_id"]),
            name=name_value,
            email=doc.get("email"),
            full_name=doc.get("full_name"),
            password_hash=doc.get("password_hash")
        )
