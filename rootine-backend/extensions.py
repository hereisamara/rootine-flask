
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials

# Load environment variables
load_dotenv()

# mongodb client
mongo_uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'),connect=False)
db = mongo_client['rootine']
users_collection = db.users
plants_collection = db.plants
gm_collection = db.growthMetrics
reminders_collection = db.reminders

# initialize firebase admin
API_KEY = 'firebase admin apikey'
cred = credentials.Certificate('service_acc_creds.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://rootine-smth.appspot.com' # own path
})

# print("apple")
# Initialize Google Cloud Storage client
service_account_path = 'service_acc_creds.json'
fstor_client = storage.Client.from_service_account_json(service_account_path)
bucket = fstor_client.get_bucket('rootine-smth.appspot.com')  # Replace with your actual storage bucket name
