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
    """Initialize the database connection"""
    global db
    db = Database.connect()
    return db

def get_database():
    """Get the database instance - now uses Singleton pattern"""
    try:
        from patterns.singleton import DatabaseSingleton
        return DatabaseSingleton.getInstance().get_database()
    except Exception as e:
        # Fallback to old method if singleton fails
        print(f"Singleton access failed: {e}, using fallback")
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
    # Use camelCase keys for the index to match Enrollment model
    enrollments.create_index([("studentId", 1), ("courseId", 1)], unique=True)
    
    assignments = db.get_collection("assignments")
    assignments.create_index("courseId")  # Note: Using camelCase to match Assignment model
    
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
            "passwordHash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "admin",
            "createdAt": datetime.utcnow(),
        }
        try:
            users.insert_one(admin)
            print("✓ Admin user created")
        except Exception as e:
            print(f"Error creating admin: {e}")
    else:
        print("Admin user already exists")

    if users.count_documents({"email": "instructor@elearning.com"}) == 0:
        instructor = {
            "_id": ObjectId(),
            "name": "John Doe",
            "email": "instructor@elearning.com",
            "passwordHash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "instructor",
            "coursesTeaching": [],
            "createdAt": datetime.utcnow(),
        }
        try:
            users.insert_one(instructor)
            print("✓ Instructor user created")
        except Exception as e:
            print(f"Error creating instructor: {e}")
    else:
        print("Instructor user already exists")

    if users.count_documents({"email": "student1@elearning.com"}) == 0:
        student1 = {
            "_id": ObjectId(),
            "name": "Alice Smith",
            "email": "student1@elearning.com",
            "passwordHash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "student",
            "enrolledCourses": [],
            "createdAt": datetime.utcnow(),
        }
        try:
            users.insert_one(student1)
            print("✓ Student1 user created")
        except Exception as e:
            print(f"Error creating student1: {e}")
    else:
        print("Student1 user already exists")

    if users.count_documents({"email": "student2@elearning.com"}) == 0:
        student2 = {
            "_id": ObjectId(),
            "name": "Bob Johnson",
            "email": "student2@elearning.com",
            "passwordHash": bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode(),
            "role": "student",
            "enrolledCourses": [],
            "createdAt": datetime.utcnow(),
        }
        try:
            users.insert_one(student2)
            print("✓ Student2 user created")
        except Exception as e:
            print(f"Error creating student2: {e}")
    else:
        print("Student2 user already exists")


def clear_database():
    """Clear all collections (for testing)"""
    db = get_database()
    if db is None:
        print("Error: Could not connect to database")
        return
    
    collections = ["users", "courses", "enrollments", "assignments", "submissions", "categories"]
    for coll_name in collections:
        try:
            count = db.get_collection(coll_name).delete_many({}).deleted_count
            print(f"✓ Cleared {count} documents from {coll_name}")
        except Exception as e:
            print(f"Error clearing {coll_name}: {e}")
    print("✓ Database cleared")


def reset_database():
    """Clear and reseed database (for testing)"""
    print("Resetting database...")
    clear_database()
    ensure_collections_and_indexes()
    print("✓ Database reset complete")


if __name__ == "__main__":
    init_db()
    ensure_collections_and_indexes()