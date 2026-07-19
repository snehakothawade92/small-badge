from database import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

users = db.users


def create_user(name, email, password, role):

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = {

        "name": name,

        "email": email,

        "password": hashed_password,

        "role": role

    }

    users.insert_one(user)


def find_user(email):

    return users.find_one({"email": email})
def verify_password(user, password):

    return bcrypt.check_password_hash(
        user["password"],
        password
    )    