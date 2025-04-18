from App.database import db
from App.models import Tenant
from App.models import Apartment
from werkzeug.security import check_password_hash, generate_password_hash

def create_tenant(username, email, password, lease_code):
    apartment = Apartment.query.filter_by(lease_code=lease_code).first()
    if not apartment:
        return None

    tenant = Tenant(
        username=username,
        email=email,
        password=password,
        lease_code=apartment.lease_code
    )
    db.session.add(tenant)
    db.session.commit()
    return tenant

def get_tenant_reviews(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return None
    return [review.get_json() for review in tenant.reviews]

def get_all_tenants():
    return Tenant.query.all()

def get_all_tenants_json():
    return [tenant.get_json() for tenant in Tenant.query.all()]