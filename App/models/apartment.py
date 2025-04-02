from App.database import db

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    reviews = db.relationship('Review', backref='apartment', lazy=True, cascade="all, delete-orphan")
    
    # Fixing Many-to-Many Relationship
    amenities = db.relationship(
        "ApartmentAmenity",
        back_populates="apartment",  # Proper back reference
        lazy=True,
        cascade="all, delete-orphan",
        overlaps="apartment_amenity_rel"
    )

    def __repr__(self):
        return f"<Apartment {self.title} - {self.location}>"
    
    def get_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "price": self.price,
            "landlord_id": self.landlord_id,
            "reviews": [review.get_json() for review in self.reviews],
            "amenities": [apartment_amenity.amenity.get_json() for apartment_amenity in self.apartment_amenities]
        }