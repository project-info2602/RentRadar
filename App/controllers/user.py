from App.database import db
from App.models.user import User
from App.models.apartment import Apartment
from App.models.review import Review
from werkzeug.security import generate_password_hash

def create_user(username, email, password, role):
    """Creates a new user and stores it in the database."""
    if role not in ['tenant', 'landlord']:
        return {"message": "Invalid role. Role must be either 'tenant' or 'landlord'."}, 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"message": "Username or email already exists."}, 400
    
    hashed_password = generate_password_hash(password, method='sha256')
    user = User(username=username, email=email, password=hashed_password, role=role)

    try:
        db.session.add(user)
        db.session.commit()
        return user  # Return the user object directly
    except Exception as e:
        db.session.rollback()
        return {"message": str(e)}, 500

def get_user_by_username(username):
    """Fetch a user by their username."""
    return User.query.filter_by(username=username).first()

def get_user(user_id):
    """Fetch a user by their ID."""
    return User.query.get(user_id)

def get_all_users():
    """Fetch all users."""
    return User.query.all()

def get_all_users_json():
    """Fetch all users as JSON."""
    return [user.get_json() for user in User.query.all()]

def update_user(user_id, username):
    """Update a user's username."""
    user = get_user(user_id)
    if user:
        user.username = username
        try:
            db.session.commit()
            return user.get_json()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500
    return {"message": "User not found."}, 404

def delete_user(user_id):
    """Delete a user by their ID."""
    user = get_user(user_id)
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500
    return {"message": "User not found."}, 404

#Landlord functions

# Get all lease codes for apartments owned by a landlord
def get_all_leasecodes_by_landlord(landlord_id):
    # Fetch all apartments that belong to the landlord
    apartments = Apartment.query.filter_by(landlord_id=landlord_id).all()

    if not apartments:
        return {"message": "No apartments found for this landlord"}, 404

    # Extract the lease codes for each apartment
    leasecodes = [apartment.leasecode for apartment in apartments]  # Assuming `leasecode` is a field in the Apartment model

    if not leasecodes:
        return {"message": "No lease codes found for this landlord"}, 404

    return {"leasecodes": leasecodes}

#Verified tenant functions
def create_review_by_verified_tenant(user_id, apartment_id, rating, comment):
    user = User.query.get(user_id)
    apartment = Apartment.query.get(apartment_id)

    if not user:
        return {"message": "User not found."}, 404
    
    if not apartment:
        return {"message": "Apartment not found."}, 404
    
    if user.role != 'tenant':
        return {"message": "Only tenants can leave reviews."}, 403

    # Ensure the tenant is verified
    if not user.is_verified:
        return {"message": "User must be a verified tenant to leave a review."}, 403

    if not (1 <= rating <= 5):
        return {"message": "Rating must be between 1 and 5."}, 400

    # Create and save the review
    review = Review(user_id=user_id, apartment_id=apartment_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    
    return review.get_json()

def update_review_by_verified_tenant(review_id, user_id, data):
    review = Review.query.get(review_id)
    if not review:
        return {"message": "Review not found."}, 404
    
    # Check if the review belongs to the user
    if review.user_id != user_id:
        return {"message": "You can only update your own reviews."}, 403
    
    if user_id:
        user = User.query.get(user_id)
        if user.role != 'tenant':
            return {"message": "Only tenants can update reviews."}, 403

        # Ensure the tenant is verified
        if not user.is_verified:
            return {"message": "User must be a verified tenant to update a review."}, 403

    # Update the review fields based on the passed data
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    
    db.session.commit()
    
    return review.get_json()

def delete_review_by_verified_tenant(review_id, user_id):
    review = Review.query.get(review_id)
    if not review:
        return {"message": "Review not found."}, 404
    
    # Check if the review belongs to the user
    if review.user_id != user_id:
        return {"message": "You can only delete your own reviews."}, 403

    if user_id:
        user = User.query.get(user_id)
        if user.role != 'tenant':
            return {"message": "Only tenants can delete reviews."}, 403

        # Ensure the tenant is verified
        if not user.is_verified:
            return {"message": "User must be a verified tenant to delete a review."}, 403

    db.session.delete(review)
    db.session.commit()
    
    return {"message": "Review deleted successfully."}
