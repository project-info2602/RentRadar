from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models import Apartment

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)

    # Import Apartment lazily inside the function or method that uses it
    @property
    def apartments(self):
        from App.models.apartment import Apartment  # Lazy import to avoid circular import
        return Apartment.query.filter_by(landlord_id=self.id).all()

    apartments_owned = db.relationship('Apartment', foreign_keys='Apartment.landlord_id', back_populates='landlord')
    rented_apartment = db.relationship('Apartment', foreign_keys='Apartment.tenant_id', back_populates='tenant', uselist=False)


    reviews = db.relationship('Review', backref='author', lazy=True)

    def __init__(self, username, email, password, role, apartment_id=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.apartment_id = apartment_id  # Store apartment ID for tenants

    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'apartment_id': self.apartment_id  # Show apartment ID
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def verify_tenant(self, lease_code):
        """Verify if a tenant belongs to an apartment using the lease code."""
        from App.models import Apartment  # Avoid circular import
        apartment = Apartment.query.filter_by(id=self.apartment_id, lease_code=lease_code).first()
        return apartment is not None  # Returns True if lease code is correct

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
