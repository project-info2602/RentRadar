from App.models import Apartment, User
from App.database import db

# Create a new apartment (only landlords can create)
def create_apartment(landlord_id, data):
    landlord = User.query.get(landlord_id)
    if landlord and landlord.role == 'landlord':
        new_apartment = Apartment(
            landlord_id=landlord_id,
            location=data['location'],
            price=data['price'],
            amenities=data['amenities']
        )
        db.session.add(new_apartment)
        db.session.commit()
        return new_apartment
    return None, "Only landlords can create apartments"

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
        apartment.amenities = data.get('amenities', apartment.amenities)
        db.session.add(apartment)
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
        query = query.filter(Apartment.amenities.contains(filters['amenities']))
    return query.all()
