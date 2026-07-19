from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Create Mongo object
mongo = PyMongo()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret123')

    # Database name MUST be included
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb://localhost:27017/smallbadge'
    )