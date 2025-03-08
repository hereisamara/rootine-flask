from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
# Replace <username>, <password>, <cluster-url>, and <database> with your details
mongo_uri =os.getenv('MONGO_URI')

client = MongoClient(mongo_uri)
db = client.get_database('plants')

# Example: List collections
collections = db.list_collection_names()
print(collections)

