from App.database import db
from App.models import Landlord
from App.controllers.apartment import create_apartment

def create_landlord(username, email, password):
    """Create a new landlord."""
    landlord = Landlord(username=username, email=email, password=password)
    #landlord.set_password(password)
    db.session.add(landlord)
    db.session.commit()
    return landlord

def add_apartment(landlord_id, title, description, location, price, amenities):
    apartment = create_apartment(title, description, location, price, landlord_id, amenities)

    return apartment

def get_landlord_apartments(landlord_id):
    """Return a list of apartments owned by a landlord."""
    landlord = Landlord.query.get(landlord_id)
    if landlord:
        return [apt.get_json() for apt in landlord.apartments_owned] if landlord else None
    return []

def get_all_landlords():
    return Landlord.query.all()

def get_all_landlords_json():
    landlords = Landlord.query.all()
    return [landlord.get_json() for landlord in landlords]  # Assuming `to_json` method exists on the `Landlord` model
