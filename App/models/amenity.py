from App.database import db

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Amenity {self.name}>"

    def get_json(self):
        """Returns the amenity information as a dictionary."""
        return {
            "id": self.id,
            "name": self.name
        }

class ApartmentAmenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey('amenity.id'), nullable=False)

    apartment = db.relationship('Apartment', backref='apartment_amenities', lazy=True)
    amenity = db.relationship('Amenity', backref='apartment_amenities', lazy=True)

    def __repr__(self):
        return f"<ApartmentAmenity Apartment {self.apartment_id} - Amenity {self.amenity_id}>"

    def get_json(self):
        """Returns apartment-amenity relationship as a dictionary with amenity name."""
        return {
            "id": self.id,
            "apartment_id": self.apartment_id,
            "amenity_id": self.amenity_id,
            "amenity_name": self.amenity.name  # Get amenity's name
        }
