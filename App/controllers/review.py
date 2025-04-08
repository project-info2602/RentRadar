from App.models import Review, Tenant, Apartment
from App.database import db

# Create a new review (only verified tenants can leave reviews)
def create_review(tenant_id, apartment_id, rating, comment):
    tenant = Tenant.query.get(tenant_id)
    apartment = Apartment.query.get(apartment_id)

    if not tenant:
        print(f"Error: Tenant {tenant_id} not found")
        return None
    
    if not apartment:
        print(f"Error: Apartment {apartment_id} not found")
        return None

    # Ensure the tenant is verified for this apartment
    if tenant.apartment_id != apartment.id:
        print(f"Error: Tenant {tenant_id} is not verified for Apartment {apartment_id}")
        return None

    if not (1 <= rating <= 5):
        print(f"Error: Rating {rating} is out of valid range (1-5)")
        return None

    review = Review(tenant_id=tenant_id, apartment_id=apartment_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return review

# Get all reviews for an apartment
def get_reviews(apartment_id):
    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    return [review.get_json() for review in reviews]  # Ensure Review model has a to_json method

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
