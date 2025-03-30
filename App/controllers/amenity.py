from App.models import Amenity
from App.database import db

# Create a new amenity
def create_amenity(data):
    new_amenity = Amenity(name=data['name'])
    db.session.add(new_amenity)
    db.session.commit()
    return new_amenity

# Get all amenities
def get_amenities():
    return Amenity.query.all()

# Delete an amenity
def delete_amenity(id):
    amenity = Amenity.query.get(id)
    if amenity:
        db.session.delete(amenity)
        db.session.commit()
        return True
    return False