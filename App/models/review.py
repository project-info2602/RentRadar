from datetime import datetime
from App.database import db

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)  # Reference to Tenant
    tenant = db.relationship('Tenant', back_populates='reviews')  # Define reverse relationship

    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)  # Reference to Apartment
    apartment = db.relationship('Apartment', back_populates='reviews')  # Define reverse relationship

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set the current time when a review is created

    def __init__(self, tenant_id, apartment_id, rating, comment):
        self.tenant_id = tenant_id
        self.apartment_id = apartment_id
        self.rating = rating
        self.comment = comment

    def get_json(self):
        """Convert the Review object to JSON format."""
        return {
            "id": self.id,
            "content": self.content,
            "rating": self.rating,
            "tenant_id": self.tenant_id,
            "apartment_id": self.apartment_id,
            "created_at": self.created_at.isoformat()  # Convert to ISO format for easier handling
        }
