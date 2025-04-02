from App.models import Review, User, Apartment
from App.database import db

# Create a new review (only verified tenants can leave reviews)
def create_review(user_id, apartment_id, rating, comment):
    review = Review(user_id=user_id, apartment_id=apartment_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return review

# Get all reviews for an apartment
def get_reviews(apartment_id):
    return Review.query.filter_by(apartment_id=apartment_id).all()

# Update a review
def update_review(id, data):
    review = Review.query.get(id)
    if review:
        review.rating = data.get('rating', review.rating)
        review.comment = data.get('comment', review.comment)
        db.session.add(review)
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