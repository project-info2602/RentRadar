from App.database import db
from App.models import Tenant

def create_tenant(username, email, password, lease_code):
    """Create a new tenant if they provide a valid lease code."""
    #apartment = Apartment.query.filter_by(lease_code=lease_code).first()
    
    #if not apartment:
    #    return None  # Invalid lease code

    tenant = Tenant(username=username, email=email, password=password, lease_code=lease_code)
    #tenant.set_password(password)  # Securely hash the password
    #tenant.apartment_id = apartment.id  # Link tenant to the apartment via foreign key

    db.session.add(tenant)
    db.session.commit()
    
    return tenant


def get_tenant_reviews(tenant_id):
    """Return all reviews written by a tenant."""
    tenant = Tenant.query.get(tenant_id)
    return [review.get_json() for review in tenant.reviews] if tenant else None

def get_all_tenants():
    return Tenant.query.all()

def get_all_tenants_json():
    tenants = Tenant.query.all()
    return [tenant.to_json() for tenant in tenants]  # Assuming `to_json` method exists on the `Tenant` model
