from App.models import Apartment, User, Amenity, ApartmentAmenity
from App.database import db

# Create a new apartment (only landlords can create)
def create_apartment(title, description, location, price, landlord_id):
    landlord = User.query.get(landlord_id)
    if not landlord:
        return {"message": "Landlord not found."}, 404
    
    if landlord.role != 'landlord':
        return {"message": "Only landlords can create apartments."}, 403

    apartment = Apartment(
        title=title,
        description=description,
        location=location,
        price=price,
        landlord_id=landlord_id
    )
    
    db.session.add(apartment)
    db.session.commit()

    return apartment

# Get all apartments
def get_apartments():
    return Apartment.query.all()

# Get apartment by ID
def get_apartment(id):
    return Apartment.query.get(id)

# Update an apartment
def update_apartment(id, data):
    apartment = Apartment.query.get(id)
    if apartment:
        apartment.location = data.get('location', apartment.location)
        apartment.price = data.get('price', apartment.price)
        apartment.description = data.get('description', apartment.description)
        
        # Update amenities (this assumes you are passing a list of amenity IDs to update)
        if 'amenities' in data:
            amenities_ids = data['amenities']
            apartment.amenities.clear()  # Remove existing amenities
            for amenity_id in amenities_ids:
                amenity = Amenity.query.get(amenity_id)
                if amenity:
                    apartment_amenity = ApartmentAmenity(apartment_id=apartment.id, amenity_id=amenity.id)
                    db.session.add(apartment_amenity)
        
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

# Search apartments by filters (location, price, amenities)
def search_apartments(filters):
    query = Apartment.query
    if filters.get('location'):
        query = query.filter(Apartment.location.like(f"%{filters['location']}%"))
    if filters.get('price'):
        query = query.filter(Apartment.price <= filters['price'])
    
    if filters.get('amenities'):
        amenities = filters['amenities']
        for amenity_id in amenities:
            # Assume amenity_id is a list of amenity IDs to filter by
            query = query.filter(Apartment.amenities.any(ApartmentAmenity.amenity_id == amenity_id))
    
    return query.all()
