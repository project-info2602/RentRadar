from App.models import ApartmentAmenity, Amenity, Apartment
from App.database import db

# Create a new amenity
def create_amenity(name):
    new_amenity = Amenity(name=name)
    db.session.add(new_amenity)
    db.session.commit()
    return new_amenity

# Get all amenities
def get_all_amenities():
    return Amenity.query.all()

# Get a specific amenity by ID
def get_amenity(id):
    return Amenity.query.get(id)

# Delete an amenity by ID
def delete_amenity(id):
    amenity = get_amenity(id)
    if amenity:
        db.session.delete(amenity)
        db.session.commit()
        return True
    return False

# Add an amenity to an apartment
def add_amenity_to_apartment(apartment_id, amenity_id):
    apartment = Apartment.query.get(apartment_id)
    amenity = Amenity.query.get(amenity_id)
    
    if apartment and amenity:
        new_apartment_amenity = ApartmentAmenity(apartment_id=apartment.id, amenity_id=amenity.id)
        db.session.add(new_apartment_amenity)
        db.session.commit()
        return new_apartment_amenity
    return None

# Get all amenities associated with an apartment
def get_amenities_for_apartment(apartment_id):
    apartment_amenities = ApartmentAmenity.query.filter_by(apartment_id=apartment_id).all()
    return [apartment_amenity.get_json() for apartment_amenity in apartment_amenities]

# Remove an amenity from an apartment
def remove_amenity_from_apartment(apartment_id, amenity_id):
    apartment_amenity = ApartmentAmenity.query.filter_by(apartment_id=apartment_id, amenity_id=amenity_id).first()
    if apartment_amenity:
        db.session.delete(apartment_amenity)
        db.session.commit()
        return True
    return False