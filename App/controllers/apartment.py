from App.models import Apartment, User
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
        # Assuming amenities is a list or a relationship
        # if amenities are part of a list, this logic should update or append accordingly
        if 'amenities' in data:
            apartment.amenities = data['amenities']  # Adjust based on your model relationship
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
