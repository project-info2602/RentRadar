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
    landlord = Landlord.query.get(landlord_id)  # Changed to Landlord model
    if not landlord:
        return {"message": "Landlord not found."}, 404

    if location not in LOCATIONS:
        return {"message": "Invalid location."}, 400

    for amenity in amenities:
        if amenity not in AMENITIES:
            return {"message": f"Invalid amenity: {amenity}"}, 400

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

    # Now generate and save lease code
    apartment.lease_code = generate_lease_code(apartment) #just added to test
    db.session.commit()                                   #just added to test

    return apartment

# Get all apartments
def get_apartments():
    return Apartment.query.all()

# Get apartment by ID
def get_apartment(id):
    return Apartment.query.get(id)

# Update an apartment's amenities from the constant list
# Update an apartment's amenities, ensuring amenities are in the constant list
def update_apartment(id, title=None, description=None, price=None, amenities_list=None):
    apartment = Apartment.query.get(id)

    if apartment:
        if title:
            apartment.title = title
        if description:
            apartment.description = description
        if price is not None:
            apartment.price = price

        if amenities_list is not None:
            # Validate amenities against allowed list
            valid_amenities = [a for a in amenities_list if a in AMENITIES]
            if not valid_amenities:
                return {"message": "No valid amenities found in the provided list."}, 400
            apartment.amenities = valid_amenities

        db.session.commit()
        return apartment
    return None


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

    # Filter by location (in SQL)
    if filters.get('location') and filters['location'] in LOCATIONS:
        query = query.filter(Apartment.location == filters['location'])

    apartments = query.all()

    # Filter by amenities (in Python)
    if filters.get('amenities'):
        selected_amenities = set(filters['amenities'])

        def has_all_amenities(apartment):
            return apartment.amenities and selected_amenities.issubset(set(apartment.amenities))

        apartments = list(filter(has_all_amenities, apartments))

    return apartments

# Get all reviews for a specific apartment
def get_reviews_for_apartment(apartment_id):
    # Query the database to fetch all reviews for the apartment
    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    
    if not reviews:
        return {"message": "No reviews found for this apartment"}, 404
    
    # Return reviews as a list of JSON objects
    return [review.get_json() for review in reviews]

# Get all tenants of a specific apartment
def get_all_tenants_of_apartment(apartment_id):
    apartment = Apartment.query.get(apartment_id)

    if not apartment:
        return {"message": "Apartment not found"}, 404

    # Get all tenants associated with this apartment via reviews (or however tenants are associated)
    tenants = Tenant.query.join(Review).filter(Review.apartment_id == apartment_id).all()  # Changed to Tenant model

    if not tenants:
        return {"message": "No tenants found for this apartment"}, 404

    # Return tenants as a list of JSON objects
    return [tenant.get_json() for tenant in tenants]

def get_apartment_via_leasecode(leasecode):
    apartment = Apartment.query.filter_by(lease_code=leasecode).first()
    if not apartment:
        return {"message": "Apartment with this lease code not found."}, 404
    return apartment