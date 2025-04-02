from App.models import ApartmentAmenity, Amenity, Apartment
from App.database import db

# Create a new amenity
def create_amenity(name):
    try:
        amenity = Amenity(name=name)
        db.session.add(amenity)
        db.session.commit()
        return amenity
    except Exception as e:
        print(f"Error creating amenity {name}: {e}")
        return None


def link_apartment_to_amenity(apartment_id, amenity_id):
    try:
        apartment_amenity = ApartmentAmenity(apartment_id=apartment_id, amenity_id=amenity_id)
        db.session.add(apartment_amenity)
        db.session.commit()
        return apartment_amenity
    except Exception as e:
        print(f"Error linking apartment {apartment_id} to amenity {amenity_id}: {e}")
        return None


# Get all amenities
def get_all_amenities():
    return Amenity.query.all()

# Get a specific amenity by ID
def get_amenity(id):
    return Amenity.query.get(id)

# Delete an amenity by ID
def delete_amenity(id):
    try:
        amenity = get_amenity(id)
        if amenity:
            db.session.delete(amenity)
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting amenity {id}: {e}")
        return False

def get_amenities_for_apartment(apartment_id):
    try:
        apartment = Apartment.query.get(apartment_id)
        if not apartment:
            return []
        
        amenities = db.session.query(Amenity).join(ApartmentAmenity).filter(ApartmentAmenity.apartment_id == apartment_id).all()
        return [amenity.name for amenity in amenities]
    except Exception as e:
        print(f"Error fetching amenities for apartment {apartment_id}: {e}")
        return []

def remove_amenity_from_apartment(apartment_id, amenity_id):
    try:
        apartment_amenity = ApartmentAmenity.query.filter_by(apartment_id=apartment_id, amenity_id=amenity_id).first()
        if apartment_amenity:
            db.session.delete(apartment_amenity)
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error removing amenity {amenity_id} from apartment {apartment_id}: {e}")
        return False