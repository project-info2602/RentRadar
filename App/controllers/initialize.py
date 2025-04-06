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
from App.constants import AMENITIES, LOCATIONS
from App.sampledata import *
import random


def initialize_sample_data_SOME():
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


def initialize_sample_data_ALL():
    try:
        # Create landlords
        
        landlords = []
        for username, email, password in LANDLORDS_DATA:
            landlord = create_landlord(username, email, password)
            if not landlord:
                raise Exception(f"Failed to create landlord {username}.")
            landlords.append(landlord)
            #print(f"Created landlord: {landlord.username}")

        # Apartments data (without amenities and location)
        
        apartments = []
        for title, description, price in APARTMENTS_DATA:
            landlord = random.choice(landlords)  # Randomly assign landlord for each apartment
            # Randomly select amenities (10 random amenities from AMENITIES list)
            selected_amenities = random.sample(AMENITIES, 10)
            # Randomly assign a location from LOCATIONS list
            location = random.choice(LOCATIONS)

            apartment = create_apartment(title, description, location, price, landlord.id, selected_amenities)
            if not apartment:
                raise Exception(f"Failed to create apartment {title}.")
            apartments.append(apartment)
            #print(f"Created apartment: {apartment.title}")
            
            # Link the apartment to amenities
            apartment.amenities = selected_amenities
            db.session.commit()
            #print(f"Linked apartment '{apartment.title}' to amenities: {', '.join(selected_amenities)}")


        for tenant_data in TENANTS_DATA:
            # Randomly select an apartment and get its lease_code
            selected_apartment = random.choice(apartments)
            lease_code = selected_apartment.lease_code  # Get the lease_code from the selected apartment

            # Create tenant with the selected lease_code
            tenant = create_tenant(tenant_data[0], tenant_data[1], tenant_data[2], lease_code=lease_code)
            if not tenant:
                print(f"Failed to create tenant {tenant_data[0]}.")
                continue  # Skip this tenant creation and move to the next one

            # Manually assign the apartment's lease_code to the tenant
            tenant.apartment = selected_apartment  # Associate the tenant with the selected apartment
            db.session.commit()
            #print(f"Created tenant: {tenant.username} and assigned to apartment: {selected_apartment.title}")

            # Randomly select a review from the predefined list
            review_message, rating = random.choice(REVIEWS_DATA)  # Randomly choose a review and its rating
            review = create_review(tenant.id, selected_apartment.id, rating, review_message)
            if not review:
                print(f"Failed to create review for tenant {tenant.username}.")
                continue  # Skip this review creation and move to the next tenant

            #print(f"Created review for tenant {tenant.username} with rating {rating} for apartment {selected_apartment.title}")

    except Exception as e:
        print(f"Error initializing sample data: {e}")


def initialize():
    db.drop_all()
    db.create_all()
    #initialize_sample_data_SOME()
    initialize_sample_data_ALL()
