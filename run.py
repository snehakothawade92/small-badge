from app import create_app
from app.db import get_db
import bcrypt
from datetime import datetime

app = create_app()

def seed_super_admin():
    """
    Seeds a default Super Admin account if none exists in the database.
    This ensures the user can log in immediately after setup.
    """
    with app.app_context():
        db = get_db()
        super_admin = db.users.find_one({"role": "super_admin"})
        
        if not super_admin:
            # Default admin credentials
            admin_email = "admin@smallbadge.com"
            admin_password = "adminpassword123"
            
            # Hash password
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
            
            db.users.insert_one({
                "name": "Platform Super Admin",
                "email": admin_email,
                "password_hash": hashed_pw,
                "role": "super_admin",
                "org_id": None,
                "status": "active",
                "created_at": datetime.utcnow()
            })
            print("\n" + "="*60)
            print("DEFAULT SUPER ADMIN ACCOUNT CREATED:")
            print(f"Email:    {admin_email}")
            print(f"Password: {admin_password}")
            print("="*60 + "\n")

if __name__ == '__main__':
    seed_super_admin()
    # Run server on port 5000 in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
