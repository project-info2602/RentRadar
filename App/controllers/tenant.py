from App.database import db
from App.models import Tenant

def create_tenant(username, email, password, lease_code):
    try:
        tenant = Tenant(username=username, email=email, password=password, lease_code=lease_code)
        db.session.add(tenant)
        db.session.commit()
        return tenant
    except ValueError as e:
        print(f"[create_tenant] Error: {e}")
        return None


def get_tenant_reviews(tenant_id):
    """Return all reviews written by a tenant."""
    tenant = Tenant.query.get(tenant_id)
    return [review.get_json() for review in tenant.reviews] if tenant else None

def get_all_tenants():
    return Tenant.query.all()

def get_all_tenants_json():
    tenants = Tenant.query.all()
    return [tenant.to_json() for tenant in tenants]  # Assuming `to_json` method exists on the `Tenant` model
