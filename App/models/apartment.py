from App.database import db
from App.constants import AMENITIES, LOCATIONS
import hashlib

class Apartment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)  # Changed from 'user.id' to 'landlord.id'
    landlord = db.relationship('Landlord', back_populates='apartments_owned')  # Changed from 'User' to 'Landlord'

    amenities = db.Column(db.PickleType, nullable=False, default=list)

    lease_code = db.Column(db.String(32), unique=True, nullable=False)
    tenants = db.relationship('Tenant', back_populates='apartment')
    reviews = db.relationship('Review', back_populates='apartment', lazy=True, cascade="all, delete-orphan")

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
            "lease_code": self.lease_code,
            "reviews": [review.get_json() for review in self.reviews],
            "amenities": self.amenities
        }

    @staticmethod
    def generate_lease_code(title, location, landlord_id):
        """Generate a unique lease verification code."""
        data = f"{title}{location}{landlord_id}".encode('utf-8')
        return hashlib.md5(data).hexdigest()[:8]

    @staticmethod
    def validate_location(location):
        """Validate if the location is in the allowed locations list."""
        if location not in LOCATIONS:
            raise ValueError(f"Invalid location: {location}. Must be one of {LOCATIONS}.")

    @staticmethod
    def validate_amenities(amenities):
        """Validate if all amenities are in the allowed amenities list."""
        invalid_amenities = [amenity for amenity in amenities if amenity not in AMENITIES]
        if invalid_amenities:
            raise ValueError(f"Invalid amenities: {invalid_amenities}. Must be one of {AMENITIES}.")

    def validate(self):
        """Run all validations before creating or updating an apartment."""
        self.validate_location(self.location)
        self.validate_amenities(self.amenities)

