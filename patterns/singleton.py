from pymongo.database import Database as MongoDatabase
from typing import Optional
import threading

class DatabaseSingleton:
    __instance: Optional['DatabaseSingleton'] = None
    __lock: threading.Lock = threading.Lock()
    __db: Optional[MongoDatabase] = None
    
    def __init__(self):
       
        if DatabaseSingleton.__instance is not None:
             raise Exception("This class is a singleton!")
        else:
             # Initialize database connection here
             from database.seed import Database
             DatabaseSingleton.__db = Database.get_db()

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

    


    def get_database(self) -> MongoDatabase:
        return self.__db
    
    def get_collection(self, collection_name: str):
        """
        Get a specific collection from the database.
        
        Args:
            collection_name (str): Name of the collection to retrieve
            
        Returns:
            Collection: MongoDB collection object
        """
        return self.__db.get_collection(collection_name)

# Convenience function for backward compatibility
def get_db_singleton():
    """
    Get the DatabaseSingleton instance.
    Convenience function for easier access.
    
    Returns:
        DatabaseSingleton: The singleton database manager instance
    """
    return DatabaseSingleton.getInstance()
