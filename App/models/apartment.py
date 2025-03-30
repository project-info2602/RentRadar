from App.database import db

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    reviews = db.relationship('Review', backref='apartment', lazy=True)
    amenities = db.relationship('ApartmentAmenity', backref='apartment', lazy=True, cascade="all, delete-orphan")

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
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "reviews": [review.get_json() for review in self.reviews],
            "amenities": [amenity.amenity.get_json() for amenity in self.amenities]
        }