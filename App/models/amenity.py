from App.database import db

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Amenity {self.name}>"

    def get_json(self):
        return {"id": self.id, "name": self.name}


class ApartmentAmenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey("apartment.id"), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey("amenity.id"), nullable=False)

    apartment = db.relationship("Apartment", backref="apartment_amenity_rel", overlaps="amenities,apartment_amenity_rel")
    amenity = db.relationship("Amenity", backref="apartment_amenity_rel")

    def __repr__(self):
        return f"<ApartmentAmenity Apartment {self.apartment_id} - Amenity {self.amenity_id}>"

    def get_json(self):
        return {
            "id": self.id,
            "apartment_id": self.apartment_id,
            "amenity": self.amenity.get_json() if self.amenity else None  # Avoid errors
        }
