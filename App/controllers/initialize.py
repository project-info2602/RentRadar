# In App/initialize.py
from App.models.landlord import Landlord
from App.models.tenant import Tenant
from App.models.apartment import Apartment
from App.models.review import Review

from App.controllers.landlord import create_landlord
from App.controllers.tenant import create_tenant
from App.controllers.apartment import create_apartment
from App.controllers.review import create_review

from App.database import db
from App.constants import AMENITIES, LOCATIONS  # Import constants from App.constant

def initialize_sample_data():
    try:
        # Create some amenities directly from the AMENITIES constant list
        selected_amenities = ['Swimming Pool', 'Gym/Fitness Center', 'Wi-Fi']

        # Validate amenities to ensure they are in the AMENITIES constant list
        for amenity in selected_amenities:
            if amenity not in AMENITIES:
                raise Exception(f"Invalid amenity: {amenity} is not in the predefined list of amenities.")

        # Create a landlord
        bob = create_landlord('bob', 'bob@bobmail.com', 'bobpass')
        if not bob:
            raise Exception("Failed to create landlord Bob.")
        print(f"Created landlord: {bob.username}")

        # Create an apartment for Bob with a location from the LOCATIONS list
        location = 'Port of Spain'  # Example location, can be randomized or selected
        if location not in LOCATIONS:
            raise Exception(f"Invalid location: {location} is not in the predefined list of locations.")

        apartment_1 = create_apartment(
            'Spacious 1-Bedroom Apartment',
            'Cozy and modern apartment with all amenities.',
            location,  # Assigned location
            1200.00,
            bob.id,
            selected_amenities
        )
        if not apartment_1:
            raise Exception("Failed to create apartment.")
        print(f"Created apartment: {apartment_1.title}")

        # Link the apartment to amenities
        apartment_1.amenities = selected_amenities
        db.session.commit()
        print(f"Linked apartment '{apartment_1.title}' to amenities: {', '.join(selected_amenities)}")

        # Generate lease code for tenant verification
        lease_code = apartment_1.lease_code
        print(f"Generated lease code for apartment '{apartment_1.title}': {lease_code}")

        # Create a tenant (requires lease code)
        tenant = create_tenant('john_doe', 'john.doe@tenantmail.com', 'johnpass', lease_code)
        if not tenant:
            raise Exception("Failed to create tenant John Doe.")
        
        # Associate the tenant with the apartment
        tenant.apartment = apartment_1  # Associate the tenant with the apartment
        db.session.commit()

        print(f"Created tenant: {tenant.username}")
        
        # Create a review for the apartment (tenant must be verified)
        review = create_review(tenant.id, apartment_1.id, 5, 'This is a great place to live!')
        if not review:
            raise Exception("Failed to create review.")
        print(f"Created review for apartment '{apartment_1.title}' with rating {review.rating}")

    except Exception as e:
        print(f"Error initializing sample data: {e}")


def initialize():
    db.drop_all()
    db.create_all()
    initialize_sample_data()
