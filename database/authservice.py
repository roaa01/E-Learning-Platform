import bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from patterns.factory import UserFactory
from models.user import User
class auth_servise:
    def __init__(self, user_collection):
        self.users = user_collection
    def sign_up(self, role, username, email, password, full_name=None):
        user = UserFactory.create_user(
            role,
            id=None,
            username=username,
            email=email,
            full_name=full_name,
            password_hash=None
        )
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user.password_hash = password_hash

        data = {
            "username": username,
            "email": email,
            "role": role,
            "full_name": full_name,
            "password_hash": password_hash,
            "created_at": datetime.now()
        }

        try:
            result = self.users.insert_one(data)
            user.id = str(result.inserted_id)
            return user
        except DuplicateKeyError:
            return None
    def log_in(self, email_or_username, password):
        user_doc = self.users.find_one({
            "$or": [
                {"email": email_or_username},
                {"username": email_or_username}
            ]
        })

        if not user_doc:
            return None

        if not bcrypt.checkpw(password.encode(), user_doc["password_hash"].encode()):
            return None

        # Create correct User object using factory
        return UserFactory.create_user(
            user_doc["role"],
            id=str(user_doc["_id"]),
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            password_hash=user_doc["password_hash"]
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
