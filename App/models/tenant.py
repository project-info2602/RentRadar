from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models.apartment import *

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)  # Reference to Apartment
    apartment = db.relationship('Apartment', back_populates='tenants')  # Define reverse relationship

    reviews = db.relationship('Review', back_populates='tenant', lazy=True, cascade="all, delete-orphan")

    def __init__(self, username, email, password, lease_code):
        self.username = username
        self.email = email
        self.set_password(password)
    
        apartment = Apartment.query.filter_by(lease_code=lease_code).first()
        if not apartment:
            raise ValueError("Invalid lease code: no apartment found.")
    
        self.apartment_id = apartment.id

    def set_password(self, password):
        """Set the tenant's password securely (hashed)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the tenant's password."""
        return check_password_hash(self.password_hash, password)

    def get_json(self):
        """Convert the Tenant object to JSON format."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "apartment_id": self.apartment_id,
        }
    

#this is how to commit
#this is also to commit