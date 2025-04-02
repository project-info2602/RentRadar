from App.models import Review, User, Apartment
from App.database import db

# Create a new review (only verified tenants can leave reviews)
def create_review(user_id, apartment_id, rating, comment):
    user = User.query.get(user_id)
    apartment = Apartment.query.get(apartment_id)

    if not user:
        print(f"Error: User {user_id} not found")
        return None
    
    if not apartment:
        print(f"Error: Apartment {apartment_id} not found")
        return None

    if user.role != 'tenant':
        print(f"Error: User {user_id} is not a tenant and cannot leave reviews")
        return None

    if not (1 <= rating <= 5):
        print(f"Error: Rating {rating} is out of valid range (1-5)")
        return None

    review = Review(user_id=user_id, apartment_id=apartment_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return review

# Get all reviews for an apartment
def get_reviews(apartment_id):
    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    return [review.to_json() for review in reviews]  # Ensure Review model has a to_json method

# Update a review
def update_review(id, data):
    review = Review.query.get(id)
    if review:
        review.rating = data.get('rating', review.rating)
        review.comment = data.get('comment', review.comment)
        db.session.commit()
        return review
    return None

# Delete a review
def delete_review(id):
    review = Review.query.get(id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return True
    return False
