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
    
    apartment.lease_code = generate_lease_code(apartment)
    
    db.session.add(apartment)
    db.session.commit()

    return apartment

# Get all apartments
def get_apartments():
    return Apartment.query.all()

# Get apartment by ID
def get_apartment(id):
    return Apartment.query.get(id)

# Update an apartment's amenities from the constant list
# Update an apartment's amenities, ensuring amenities are in the constant list
def update_apartment_amenities(id, amenities_list):
    apartment = Apartment.query.get(id)
    
    if apartment:
        # Filter amenities to ensure they are in the constant list
        valid_amenities = [amenity for amenity in amenities_list if amenity in AMENITIES]
        
        # If no valid amenities were found, return a message
        if not valid_amenities:
            return {"message": "No valid amenities found in the provided list."}, 400
        
        # Update the apartment's amenities field
        apartment.amenities = valid_amenities
        
        # Commit the changes
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

# Verify tenant by lease code
def verify_tenant(user_id, lease_code):
    tenant = Tenant.query.get(user_id)  # Changed to Tenant model
    if not tenant:
        return {"message": "Tenant not found."}, 404
    
    apartment = Apartment.query.filter_by(lease_code=lease_code).first()
    if not apartment:
        return {"message": "Invalid lease code."}, 400
    
    if tenant in apartment.tenants:
        return {"message": "Tenant is already verified."}, 400
    
    # Create a new verified tenant (add tenant to apartment's tenant list)
    apartment.tenants.append(tenant)
    db.session.commit()

    return {"message": "Tenant verified successfully."}

# Search apartments by location and amenities
def search_apartments(filters):
    query = Apartment.query
    
    if filters.get('location') and filters['location'] in LOCATIONS:
        query = query.filter(Apartment.location == filters['location'])
    
    if filters.get('amenities'):
        selected_amenities = set(filters['amenities'])
        query = query.filter(Apartment.amenities.contains(selected_amenities))
    
    return query.all()

# Get all reviews for a specific apartment
def get_reviews_for_apartment(apartment_id):
    # Query the database to fetch all reviews for the apartment
    reviews = Review.query.filter_by(apartment_id=apartment_id).all()
    
    if not reviews:
        return {"message": "No reviews found for this apartment"}, 404
    
    # Return reviews as a list of JSON objects
    return [review.to_json() for review in reviews]

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
