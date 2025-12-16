from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import bcrypt

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "elearning_platform")

class Database:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB"""
        try:
            cls._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            cls._client.admin.command('ping')
            cls._db = cls._client[DB_NAME]
            print(f"Connected to MongoDB: {DB_NAME}")
            return cls._db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Failed to connect to MongoDB: {e}")
            return None

    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def close(cls):
        """Close database connection"""
        if cls._client:
            cls._client.close()
            print("✓ MongoDB connection closed")

db = None

def init_db():
    "Initialize the database connection"
    global db
    db = Database.connect()
    return db

def get_database():
    "Get the database instance"
    global db
    if db is None:
        db = Database.connect()
    return db

def ensure_collections_and_indexes():
    "Create collections and indexes"
    db = get_database()
    if db is None:
        print("Error: Could not connect to MongoDB. Collections and indexes will not be created.")
        return
    
    users = db.get_collection("users")
    users.create_index("email", unique=True)
    
    courses = db.get_collection("courses")
    # Remove old slug index if it exists to avoid duplicate key errors with null values
    try:
        courses.drop_index("slug_1")
    except Exception:
        pass
    # Create index on id field instead for faster lookups
    courses.create_index("id", unique=True)
    
    enrollments = db.get_collection("enrollments")
    # Drop old index if it exists
    try:
        enrollments.drop_index("user_id_1_course_id_1")
    except Exception:
        pass
    enrollments.create_index([("student_id", 1), ("course_id", 1)], unique=True)
    
    assignments = db.get_collection("assignments")
    assignments.create_index("courseId")
    
    # migrate any existing plaintext passwords to hashed field, then seed
    migrate_plain_passwords()
    seed_initial_data()

def seed_initial_data():
    "Seed initial admin user and sample data"
    db = get_database()
    users = db.get_collection("users")
    
    if users.count_documents({"email": "admin@elearning.com"}) == 0:
        admin = {
            "_id": ObjectId(),
            "name": "admin",
            "email": "admin@elearning.com",
            "password_hash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "admin",
            "created_at": datetime.utcnow(),
        }
        users.insert_one(admin)
    else:
        print("Admin user already exists")

    if users.count_documents({"email": "instructor@elearning.com"}) == 0:
        instructor = {
            "_id": ObjectId(),
            "name": "John Doe",
            "email": "instructor@elearning.com",
            "password_hash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "instructor",
            "courses_teaching": [],
            "created_at": datetime.utcnow(),
        }
        users.insert_one(instructor)
    else:
        print("Instructor user already exists")

    if users.count_documents({"email": "student1@elearning.com"}) == 0:
        student1 = {
            "_id": ObjectId(),
            "name": "Alice Smith",
            "email": "student1@elearning.com",
            "password_hash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "student",
            "enrolled_courses": [],
            "created_at": datetime.utcnow(),
        }
        users.insert_one(student1)
    else:
        print("Student1 user already exists")

    if users.count_documents({"email": "student2@elearning.com"}) == 0:
        student2 = {
            "_id": ObjectId(),
            "name": "Bob Johnson",
            "email": "student2@elearning.com",
            "password_hash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "student",
            "enrolled_courses": [],
            "created_at": datetime.utcnow(),
        }
        users.insert_one(student2)
    else:
        print("Student2 user already exists")


def migrate_plain_passwords():
    """Find documents with plaintext 'password' field, hash them into 'password_hash' and remove 'password'."""
    db = get_database()
    if db is None:
        return
    users = db.get_collection("users")
    docs = list(users.find({"password": {"$exists": True}}))
    if not docs:
        return
    for d in docs:
        plain = d.get("password")
        if not plain:
            continue
        try:
            ph = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
            users.update_one({"_id": d["_id"]}, {"$set": {"password_hash": ph}, "$unset": {"password": ""}})
            print(f"Migrated password for user {d.get('email') or d.get('_id')}")
        except Exception as e:
            print(f"Failed to migrate user {d.get('email') or d.get('_id')}: {e}")


if __name__ == "__main__":
    init_db()
    ensure_collections_and_indexes()