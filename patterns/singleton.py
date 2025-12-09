from database_manager import DatabaseManager
from bson import ObjectId
from datetime import datetime

class EnrollmentManager:
    def __init__(self):
        self.db = DatabaseManager().get_collection("enrollments")
