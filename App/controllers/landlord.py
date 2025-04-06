from App.database import db
from App.models import Landlord, Apartment

def create_landlord(username, email, password):
    """Create a new landlord."""
    landlord = Landlord(username=username, email=email, password=password)
    #landlord.set_password(password)
    db.session.add(landlord)
    db.session.commit()
    return landlord

def add_apartment(landlord_id, title, description, location, price, amenities):
    """Allow landlords to add a new apartment."""
    lease_code = Apartment.generate_lease_code(title, location, landlord_id)
    apartment = Apartment(
        title=title,
        description=description,
        location=location,
        price=price,
        landlord_id=landlord_id,
        amenities=amenities,
        lease_code=lease_code
    )
    db.session.add(apartment)
    db.session.commit()
    return apartment

def get_landlord_apartments(landlord_id):
    """Return a list of apartments owned by a landlord."""
    landlord = Landlord.query.get(landlord_id)
    return [apt.get_json() for apt in landlord.apartments_owned] if landlord else None

def get_all_landlords():
    return Landlord.query.all()

def get_all_landlords_json():
    landlords = Landlord.query.all()
    return [landlord.to_json() for landlord in landlords]  # Assuming `to_json` method exists on the `Landlord` model
