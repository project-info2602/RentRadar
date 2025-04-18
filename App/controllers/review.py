from App.models import Review, Tenant, Apartment
from App.database import db

# Create a new review (only verified tenants can leave reviews)
def create_review(tenant_id, apartment_id, rating, comment):
    tenant = Tenant.query.get(tenant_id)
    apartment = Apartment.query.get(apartment_id)

    if not tenant or not apartment:
        return None

    if tenant.apartment_id != apartment.id:
        return None

    if not (1 <= rating <= 5):
        return None

    review = Review(
        tenant_id=tenant_id,
        apartment_id=apartment_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    return review

# Get all reviews for an apartment
def get_reviews(apartment_id):
    return [review.get_json() for review in Review.query.filter_by(apartment_id=apartment_id).all()]

# Update a review
def update_review(id, data):
    review = Review.query.get(id)
    if not review:
        return None

    if 'rating' in data and (1 <= data['rating'] <= 5):
        review.rating = data['rating']

    if 'comment' in data:
        review.comment = data['comment']

    db.session.commit()
    return review

# Delete a review
def delete_review(id):
    review = Review.query.get(id)
    if not review:
        return False

    db.session.delete(review)
    db.session.commit()
    return True