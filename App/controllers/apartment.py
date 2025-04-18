from App.models import Apartment, Landlord, Tenant, Review
from App.database import db
from App.constants import AMENITIES, LOCATIONS
import hashlib

# Function to generate a unique lease code
def generate_lease_code(apartment):
    data = f"{apartment.id}{apartment.title}{apartment.location}{apartment.price}"
    return hashlib.md5(data.encode()).hexdigest()[:8]

# Create a new apartment (only landlords can create)
def create_apartment(title, description, location, price, landlord_id, amenities):
    landlord = Landlord.query.get(landlord_id)
    if not landlord:
        return None

    if location not in LOCATIONS:
        return None

    for amenity in amenities:
        if amenity not in AMENITIES:
            return None

    apartment = Apartment(
        title=title,
        description=description,
        location=location,
        price=price,
        landlord_id=landlord_id,
        amenities=amenities
    )

    db.session.add(apartment)
    db.session.commit()

    apartment.lease_code = generate_lease_code(apartment)
    db.session.commit()

    return apartment

# Get all apartments
def get_apartments():
    return Apartment.query.all()

# Get apartment by ID
def get_apartment(id):
    return Apartment.query.get(id)

# Update an apartment's amenities, ensuring amenities are in the constant list
def update_apartment(id, title=None, description=None, price=None, amenities_list=None):
    apartment = Apartment.query.get(id)

    if not apartment:
        return None

    if title:
        apartment.title = title
    if description:
        apartment.description = description
    if price is not None:
        apartment.price = price

    if amenities_list is not None:
        valid_amenities = [a for a in amenities_list if a in AMENITIES]
        if not valid_amenities:
            return None
        apartment.amenities = valid_amenities

    db.session.commit()
    return apartment

# Delete an apartment
def delete_apartment(id):
    apartment = Apartment.query.get(id)
    if apartment:
        db.session.delete(apartment)
        db.session.commit()
        return True
    return False

def is_tenant_verified(tenant_id, lease_code):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return False

    apartment = Apartment.query.filter_by(lease_code=lease_code).first()
    if not apartment:
        return False

    return tenant in apartment.tenants and apartment.id == tenant.apartment_id

def search_apartments(filters):
    query = Apartment.query

    if filters.get('location') and filters['location'] in LOCATIONS:
        query = query.filter(Apartment.location == filters['location'])

    apartments = query.all()

    if filters.get('amenities'):
        selected_amenities = set(filters['amenities'])

        def has_all_amenities(apartment):
            return apartment.amenities and selected_amenities.issubset(set(apartment.amenities))

        apartments = list(filter(has_all_amenities, apartments))

    return apartments

# Get all reviews for a specific apartment
def get_reviews_for_apartment(apartment_id):
    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    if not reviews:
        return None
    return [review.get_json() for review in reviews]

# Get all tenants of a specific apartment
def get_all_tenants_of_apartment(apartment_id):
    apartment = Apartment.query.get(apartment_id)
    if not apartment:
        return None

    tenants = Tenant.query.join(Review).filter(Review.apartment_id == apartment_id).all()
    if not tenants:
        return None

    return [tenant.get_json() for tenant in tenants]

def get_apartment_via_leasecode(leasecode):
    return Apartment.query.filter_by(lease_code=leasecode).first()
