from App.database import db
from App.models import Landlord
from App.controllers.apartment import create_apartment

def create_landlord(username, email, password):
    landlord = Landlord(username=username, email=email, password=password)
    db.session.add(landlord)
    db.session.commit()
    return landlord

def add_apartment(landlord_id, title, description, location, price, amenities):
    return create_apartment(title, description, location, price, landlord_id, amenities)

def get_landlord_apartments(landlord_id):
    landlord = Landlord.query.get(landlord_id)
    if not landlord:
        return None
    return [apt.get_json() for apt in landlord.apartments_owned]

def get_all_landlords():
    return Landlord.query.all()

def get_all_landlords_json():
    return [landlord.get_json() for landlord in Landlord.query.all()]
