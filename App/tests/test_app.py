import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import Landlord, Tenant, Apartment, Review
from App.constants import AMENITIES, LOCATIONS
from App.controllers import (

    create_landlord,
    add_apartment,
    get_landlord_apartments,
    get_all_landlords_json,
    create_tenant,
    get_tenant_reviews,
    get_all_tenants_json,
    create_apartment, 
    update_apartment, 
    delete_apartment, 
    verify_tenant, 
    search_apartments, 
    get_reviews_for_apartment, 
    get_all_tenants_of_apartment
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests for Landlord Model and Controller
'''

class LandlordUnitTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_landlord(self):
        """Test that a landlord is created successfully."""
        landlord = create_landlord("charlie", "charlie@example.com", "charliepass")

        # Check if the landlord is created with the correct data
        self.assertEqual(landlord.username, "charlie")
        self.assertEqual(landlord.email, "charlie@example.com")
        self.assertTrue(check_password_hash(landlord.password_hash, "charliepass"))

    def test_get_landlord_json(self):
        """Test the JSON representation of a landlord."""
        landlord = create_landlord("dave", "dave@example.com", "davepass")
        apartment1 = add_apartment(landlord.id, "Cozy Apartment", "A lovely apartment", LOCATIONS[4], 1500.00, [AMENITIES[0], AMENITIES[1]])
        apartment2 = add_apartment(landlord.id, "Cozy Apartment", "A lovely apartment", LOCATIONS[3], 1400.00, [AMENITIES[1], AMENITIES[4]])
        landlord_json = landlord.get_json()
        
        self.assertDictEqual(landlord_json, {
            'id': landlord.id,  # ID will be assigned after the database commit
            'username': "dave",
            'email': "dave@example.com",
            'owned_apartments': [apartment1.id, apartment2.id]  # No apartments owned yet
        })

    def test_add_apartment(self):
        """Test that a landlord can add an apartment."""
        landlord = create_landlord("eve", "eve@example.com", "evepass")
        apartment = add_apartment(landlord.id, "Cozy Apartment", "A lovely apartment", LOCATIONS[4], 1500.00, [AMENITIES[0], AMENITIES[1]])

        # Verifying the apartment attributes
        self.assertEqual(apartment.title, "Cozy Apartment")
        self.assertEqual(apartment.location, LOCATIONS[4])
        self.assertEqual(apartment.price, 1500.00)
        self.assertEqual(apartment.landlord_id, landlord.id)
        self.assertIn(AMENITIES[0], apartment.amenities)
        self.assertIn(AMENITIES[1], apartment.amenities)

    def test_get_landlord_apartments(self):
        """Test retrieving all apartments owned by a landlord."""
        landlord = create_landlord("frank", "frank@example.com", "frankpass")
        apartment1 = add_apartment(landlord.id, "Apartment 1", "Nice place", LOCATIONS[4], 1200.00, [AMENITIES[0]])
        apartment2 = add_apartment(landlord.id, "Apartment 2", "Cozy place", LOCATIONS[4], 1300.00, [AMENITIES[0]])

        apartments = get_landlord_apartments(landlord.id)
        
        self.assertEqual(len(apartments), 2)
        self.assertEqual(apartments[0]["title"], "Apartment 1")
        self.assertEqual(apartments[1]["title"], "Apartment 2")

    def test_get_all_landlords_json(self):
        """Test getting all landlords as JSON."""
        landlord1 = create_landlord("george", "george@example.com", "georgepass")
        landlord2 = create_landlord("hannah", "hannah@example.com", "hannahpass")
        
        landlords_json = get_all_landlords_json()
        
        # Verify that the JSON representation contains the landlords' data
        self.assertEqual(len(landlords_json), 2)
        self.assertEqual(landlords_json[0]['username'], "george")
        self.assertEqual(landlords_json[1]['username'], "hannah")


   #Unit Tests for Tenant Model and Controller


class TenantUnitTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_tenant(self):
        """Test that a tenant is created successfully."""
        landlord = create_landlord("charlie", "charlie@example.com", "charliepass")
        apartment = add_apartment(landlord.id, "Apartment 1", "Nice place", LOCATIONS[0], 1200.00, [AMENITIES[0], AMENITIES[2]])
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("john_doe", "john_doe@example.com", "johnpass", apartment.lease_code)

        self.assertEqual(tenant.username, "john_doe")
        self.assertEqual(tenant.email, "john_doe@example.com")
        self.assertEqual(tenant.apartment_id, apartment.id)
        self.assertTrue(check_password_hash(tenant.password_hash, "johnpass"))

    def test_create_tenant_invalid_lease_code(self):
        """Test that creating a tenant with an invalid lease code raises an error."""
        with self.assertRaises(ValueError) as context:
            create_tenant("jane_doe", "jane_doe@example.com", "janepass", "invalid_code")
        self.assertEqual(str(context.exception), "Invalid lease code: no apartment found.")

    def test_get_tenant_json(self):
        """Test the JSON representation of a tenant."""
        landlord = create_landlord("maria", "maria@example.com", "mariapass")
        apartment = add_apartment(landlord.id, "Luxury Apt", "Luxury apartment", LOCATIONS[0], 2000.00, [AMENITIES[0], AMENITIES[2]])
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("elena_ross", "elena_ross@example.com", "elenapass", apartment.lease_code)
        
        tenant_json = tenant.to_json()
        
        self.assertDictEqual(tenant_json, {
            'id': tenant.id,
            'username': "elena_ross",
            'email': "elena_ross@example.com",
            'apartment_id': apartment.id,
        })

    def test_get_tenant_reviews(self):
        """Test retrieving all reviews written by a tenant."""
        landlord = create_landlord("greg", "greg@example.com", "gregpass")
        apartment = add_apartment(landlord.id, "Big Apartment", "Spacious apartment", LOCATIONS[0], 1500.00, [AMENITIES[0], AMENITIES[2]])
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("bob_jones", "bob_jones@example.com", "bobpass", apartment.lease_code)

        review = Review(tenant_id=tenant.id, apartment_id=apartment.id, comment="Great place to live!", rating=5)
        db.session.add(review)
        db.session.commit()

        reviews = get_tenant_reviews(tenant.id)
        
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['comment'], "Great place to live!")


   #Unit Tests for Apartment Model and Controller


class ApartmentFunctionsTestCase(unittest.TestCase):
    """Test functions related to apartments"""

    def setUp(self):
        """Set up the test environment."""
        app = create_app('testing')
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test landlord and tenant
        self.landlord = Landlord(
            username="landlord1",
            email="landlord1@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(self.landlord)
        db.session.commit()

        self.tenant = Tenant(
            username="tenant1",
            email="tenant1@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(self.tenant)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_create_apartment(self):
        """Test apartment creation."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi", "Pool"]
        )
        self.assertIsNotNone(apartment.id)
        self.assertEqual(apartment.title, "Test Apartment")
        self.assertEqual(apartment.location, LOCATIONS[0])  # Ensure correct location

    def test_update_apartment(self):
    
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )

    # Updating the apartment amenities
        updated_apartment = update_apartment(
            apartment.id, 
            title="Updated Test Apartment", 
            description="Updated Test Description", 
            price=1200.0, 
            amenities=["Pool", "Gym"]
        )

        # Check if the apartment is updated correctly
        self.assertEqual(updated_apartment.title, "Updated Test Apartment")
        self.assertEqual(updated_apartment.description, "Updated Test Description")
        self.assertEqual(updated_apartment.price, 1200.0)  # Verify updated price
        self.assertEqual(updated_apartment.amenities, ["Pool", "Gym"])  # Verify amenities updated


    def test_delete_apartment(self):
        """Test deleting an apartment."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        apartment_id = apartment.id
        delete_apartment(apartment_id)
        apartment = Apartment.query.get(apartment_id)
        self.assertIsNone(apartment)  # Should be None since it was deleted

    def test_search_apartments(self):
        """Test searching for apartments."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location="Test Location", 
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        apartments = search_apartments(location="Test Location", amenities=["WiFi"])
        self.assertEqual(len(apartments), 1)  # Should return 1 apartment
        self.assertEqual(apartments[0].title, "Test Apartment")



if __name__ == '__main__':
    unittest.main()