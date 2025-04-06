from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)  # Reference to Apartment
    apartment = db.relationship('Apartment', back_populates='tenants')  # Define reverse relationship

    reviews = db.relationship('Review', back_populates='tenant', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Set the tenant's password securely (hashed)."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check the tenant's password."""
        return check_password_hash(self.password, password)

    def to_json(self):
        """Convert the Tenant object to JSON format."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "apartment_id": self.apartment_id,
        }
