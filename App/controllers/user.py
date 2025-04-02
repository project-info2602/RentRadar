from App.database import db
from App.models.user import *

def create_user(username, email, password, role):
    """Creates a new user and stores it in the database."""
    
    # Check if the role is valid
    if role not in ['tenant', 'landlord']:
        return {"message": "Invalid role. Role must be either 'tenant' or 'landlord'."}, 400

    # Check if the username or email already exists
    if User.query.filter_by(username=username).first():
        return {"message": "Username already exists"}, 400
    if User.query.filter_by(email=email).first():
        return {"message": "Email already exists"}, 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password, method='sha256')

    # Create the user object
    user = User(username=username, email=email, password=hashed_password, role=role)

    # Add user to the session and commit
    db.session.add(user)
    db.session.commit()

    # Return the response with user data
    return user


def get_user_by_username(username):
    """Fetch a user by their username."""
    return User.query.filter_by(username=username).first()

def get_user(id):
    """Fetch a user by their ID."""
    return User.query.get(id)

def get_all_users():
    """Fetch all users."""
    return User.query.all()

def get_all_users_json():
    """Fetch all users as JSON."""
    users = User.query.all()
    if not users:
        return []
    return [user.get_json() for user in users]

def update_user(id, username):
    """Update a user's username."""
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        db.session.commit()
        return user.get_json()  # Return the updated user data
    return None

def delete_user(id):
    """Delete a user by their ID."""
    user = get_user(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False
