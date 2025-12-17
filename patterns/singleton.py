"""
Singleton Pattern Implementation matching the UML Diagram
"""
from pymongo.database import Database as MongoDatabase
from typing import Optional
import threading

class DatabaseSingleton:
    """
    Singleton class for managing database connection.
    Reflects the 'SingleObject' from the UML diagram.
    """
    # -instance: SingleObject (Private static variable)
    __instance: Optional['DatabaseSingleton'] = None
    __lock: threading.Lock = threading.Lock()
    __db: Optional[MongoDatabase] = None
    
    # -SingleObject() (Private constructor)
    def __init__(self):
        """
        Private constructor. 
        In Python, we cannot make it truly private, but we can allow it 
        to be called only from within getInstance.
        """
        if DatabaseSingleton.__instance is not None:
             raise Exception("This class is a singleton!")
        else:
             # Initialize database connection here
             from database.seed import Database
             DatabaseSingleton.__db = Database.get_db()

    # +getInstance(): SingleObject
    @staticmethod
    def getInstance():
        """
        Static method to get the single instance of the class.
        Matches the UML +getInstance() method.
        """
        if DatabaseSingleton.__instance is None:
            with DatabaseSingleton.__lock:
                if DatabaseSingleton.__instance is None:
                    DatabaseSingleton.__instance = DatabaseSingleton()
        return DatabaseSingleton.__instance

    # +showMessage(): void
    def showMessage(self):
        """
        Demonstration method matching the UML.
        """
        print("Hello from DatabaseSingleton! Database is connected.")
        if self.__db is not None:
             print(f"Database Name: {self.__db.name}")

    # Additional utility methods for actual usage
    def get_database(self) -> MongoDatabase:
        return self.__db
    
    def get_collection(self, collection_name: str):
        return self.__db.get_collection(collection_name)


