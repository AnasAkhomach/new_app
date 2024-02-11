from pymongo import MongoClient
from contextlib import contextmanager
import os
from dotenv import load_dotenv

class MongoDBClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Ensure initialization happens only once
            self._initialize_client()

    def _initialize_client(self):
        load_dotenv()  # Load environment variables from .env file
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "myappdb")
        
        try:
            # Configuring MongoClient with connection pooling parameters
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, maxPoolSize=50)
            self.db = self.client[DATABASE_NAME]
            # Perform a quick operation to check the connection is valid
            self.client.server_info()
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None
        else:
            self.initialized = True  # Mark as initialized only if connection succeeds

    @classmethod
    def get_client(cls):
        # Ensure MongoDBClient is initialized before returning the client
        if not cls._instance:
            cls()
        return cls._instance.client

    @classmethod
    def get_db(cls):
        # Ensure MongoDBClient is initialized before returning the db
        if not cls._instance:
            cls()
        return cls._instance.db

# MongoDB Transaction Manager
class MongoDBTransactionManager:
    @staticmethod
    @contextmanager
    def transaction():
        client = MongoDBClient.get_client()
        session = client.start_session()
        session.start_transaction()
        try:
            yield session
        except Exception as e:
            print(f"Transaction error: {e}")
            session.abort_transaction()
            raise
        else:
            session.commit_transaction()
        finally:
            session.end_session()

# Example Usage
if __name__ == "__main__":
    with MongoDBTransactionManager.transaction() as session:
        db = MongoDBClient.get_db()
        # Perform transactional operations here, e.g.,
        # db.myCollection.insert_one({"key": "value"}, session=session)
