from App.database import db

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Amenity {self.name}>"

class ApartmentAmenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenity.id'), nullable=False)

    def __repr__(self):
        return f"<ApartmentAmenity Apartment {self.apartment_id} - Amenity {self.amenity_id}>"

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name
    }