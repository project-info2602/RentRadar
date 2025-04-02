from App.models.user import User
from App.models.amenity import Amenity, ApartmentAmenity
from App.models.apartment import Apartment
from App.models.review import Review

from App.controllers.user import create_user
from App.controllers.amenity import create_amenity, link_apartment_to_amenity
from App.controllers.apartment import create_apartment
from App.controllers.review import create_review

from App.database import db

def initialize_sample_data():
    try:
        # Create some amenities
        pool = create_amenity('Swimming Pool')
        gym = create_amenity('Gym')

        if pool and gym:
            print(f"Created amenities: {pool.name}, {gym.name}")
        else:
            raise Exception("Failed to create amenities.")

        # Create a user (landlord)
        bob = create_user('bob', 'bob@bobmail.com', 'bobpass', 'landlord')
        if not bob:
            raise Exception("Failed to create user Bob.")
        print(f"Created user: {bob.username}")

        # Create an apartment for Bob
        apartment_1 = create_apartment(
            'Spacious 1-Bedroom Apartment',
            'Cozy and modern apartment with all amenities.',
            '456 Oak St, Cityville',
            1200.00,
            bob.id
        )
        if not apartment_1:
            raise Exception("Failed to create apartment.")
        print(f"Created apartment: {apartment_1.title}")

        # Link the apartment to amenities
        if pool and gym:
            link_apartment_to_amenity(apartment_1.id, pool.id)
            link_apartment_to_amenity(apartment_1.id, gym.id)
            print(f"Linked apartment '{apartment_1.title}' to amenities '{pool.name}' and '{gym.name}'")

        # Create a review for the apartment
        tenant = create_user('john_doe', 'john.doe@tenantmail.com', 'johnpass', 'tenant')
        if not tenant:
            raise Exception("Failed to create tenant John Doe.")
        print(f"Created tenant: {tenant.username}")

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
