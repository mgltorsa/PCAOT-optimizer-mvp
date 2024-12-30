from datetime import datetime
from pymongo import MongoClient
from typing import Dict, Any
import os

def load_mongo_client() -> MongoClient:
    connection_string = os.environ.get("MONGO_URI")
    client = MongoClient(connection_string)
    return client

def save_to_mongodb(result: Dict[str, Any], 
                    client: MongoClient,
                    collection_name: str = "executions") -> None:
    """
    Save the execution results to MongoDB
    """
    db_name= os.environ.get("MONGO_DB_NAME")
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_one(result)