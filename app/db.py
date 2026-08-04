from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_login import UserMixin

# Global database variables
client = None
db = None

def init_db(app):
    """
    Initializes the MongoDB client and references the database defined in Config.
    Also creates necessary indexes for user and badge tables.
    """
    global client, db
    mongo_uri = app.config['MONGO_URI']
    
    # Connect client
    client = MongoClient(mongo_uri)
    
    # Extract database name from URI, e.g. "mongodb://localhost:27017/smallbadge" -> "smallbadge"
    db_name = mongo_uri.split('/')[-1]
    if '?' in db_name:
        db_name = db_name.split('?')[0]
        
    db = client[db_name]
    
    # Create critical unique indexes to enforce data integrity
    db.users.create_index("email", unique=True)
    db.organizations.create_index("name", unique=True)
    db.issued_badges.create_index("badge_id", unique=True)
    
    # Print status to terminal for dev verification
    app.logger.info(f"Successfully connected to MongoDB database: {db_name}")
    return db

def get_db():
    """Returns the database reference."""
    return db

class User(UserMixin):
    """
    Flask-Login compatible User model that interfaces with MongoDB 'users' collection.
    """
    def __init__(self, user_dict):
        self.id = str(user_dict['_id'])
        self.name = user_dict.get('name')
        self.email = user_dict.get('email')
        self.role = user_dict.get('role') # 'super_admin', 'org_admin', 'student'
        self.org_id = user_dict.get('org_id') # ObjectId reference if org_admin or student
        self.status = user_dict.get('status', 'pending') # 'pending', 'active', 'suspended'

    @staticmethod
    def get_by_id(user_id):
        """Loads a user by their MongoDB ObjectId."""
        if not db or not user_id:
            return None
        try:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except Exception:
            return None
        return None

    @staticmethod
    def get_by_email(email):
        """Loads a user by their unique email address."""
        if not db or not email:
            return None
        user_data = db.users.find_one({"email": email.strip().lower()})
        if user_data:
            return User(user_data)
        return None
