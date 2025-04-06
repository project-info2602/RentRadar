from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationship: A landlord owns multiple apartments
    apartments_owned = db.relationship('Apartment', back_populates='landlord', cascade="all, delete-orphan")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return f'Landlord {self.username} - {self.email}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'owned_apartments': [apt.id for apt in self.apartments_owned]  # List of apartment IDs
        }
