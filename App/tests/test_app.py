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
    update_apartment_amenities, 
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

    def test_create_landlord(self):
        """Test that a landlord is created successfully."""
        landlord = create_landlord("alice", "alice@example.com", "alicepass")

        # Check if the landlord is created with the correct data
        self.assertEqual(landlord.username, "alice")
        self.assertEqual(landlord.email, "alice@example.com")
        self.assertTrue(check_password_hash(landlord, "alicepass"))

    def test_get_landlord_json(self):
        """Test the JSON representation of a landlord."""
        landlord = create_landlord("bob", "bob@example.com", "bobpass")
        
        landlord_json = landlord.get_json()
        
        self.assertDictEqual(landlord_json, {
            'id': None,  # ID will be assigned after the database commit
            'username': "bob",
            'email': "bob@example.com",
            'owned_apartments': []  # No apartments owned yet
        })

    def test_add_apartment(self):
        """Test that a landlord can add an apartment."""
        landlord = create_landlord("charlie", "charlie@example.com", "charliepass")
        apartment = add_apartment(landlord.id, "Cozy Apartment", "A lovely apartment", "Arima", 1500.00, ["Gym", "Pool"])

        # Verifying the apartment attributes
        self.assertEqual(apartment.title, "Cozy Apartment")
        self.assertEqual(apartment.location, "Arima")
        self.assertEqual(apartment.price, 1500.00)
        self.assertEqual(apartment.landlord_id, landlord.id)
        self.assertIn("Gym", apartment.amenities)
        self.assertIn("Pool", apartment.amenities)

    def test_get_landlord_apartments(self):
        """Test retrieving all apartments owned by a landlord."""
        landlord = create_landlord("dave", "dave@example.com", "davepass")
        apartment1 = add_apartment(landlord.id, "Apartment 1", "Nice place", "Arima", 1200.00, ["Gym"])
        apartment2 = add_apartment(landlord.id, "Apartment 2", "Cozy place", "Arima", 1300.00, ["Pool"])

        apartments = get_landlord_apartments(landlord.id)
        
        self.assertEqual(len(apartments), 2)
        self.assertEqual(apartments[0]["title"], "Apartment 1")
        self.assertEqual(apartments[1]["title"], "Apartment 2")

    def test_get_all_landlords_json(self):
        """Test getting all landlords as JSON."""
        landlord1 = create_landlord("eve", "eve@example.com", "evepass")
        landlord2 = create_landlord("frank", "frank@example.com", "frankpass")
        
        landlords_json = get_all_landlords_json()
        
        # Verify that the JSON representation contains the landlords' data
        self.assertEqual(len(landlords_json), 2)
        self.assertEqual(landlords_json[0]['username'], "eve")
        self.assertEqual(landlords_json[1]['username'], "frank")

'''
   #Unit Tests for Tenant Model and Controller


class TenantUnitTests(unittest.TestCase):

    def test_create_tenant(self):
        """Test that a tenant is created successfully."""
        # Create an apartment first to link to the tenant
        apartment = Apartment(title="Studio Apt", description="Small apartment", location="789 Pine St", price=1000.00, lease_code="12345")
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("jane_doe", "jane_doe@example.com", "janepass", "12345")

        # Check if the tenant is created with the correct data
        self.assertEqual(tenant.username, "jane_doe")
        self.assertEqual(tenant.email, "jane_doe@example.com")
        self.assertEqual(tenant.apartment_id, apartment.id)
        self.assertTrue(check_password_hash(tenant.password, "janepass"))

    def test_create_tenant_invalid_lease_code(self):
        """Test that creating a tenant with an invalid lease code raises an error."""
        try:
            create_tenant("john_doe", "john_doe@example.com", "johnpass", "invalid_code")
            self.fail("Expected an error when creating a tenant with an invalid lease code")
        except ValueError as e:
            self.assertEqual(str(e), "Invalid lease code: no apartment found.")

    def test_get_tenant_json(self):
        """Test the JSON representation of a tenant."""
        apartment = Apartment(title="Luxury Apt", description="Luxury apartment", location="123 Maple St", price=2000.00, lease_code="98765")
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("alice_smith", "alice_smith@example.com", "alicepass", "98765")
        
        tenant_json = tenant.to_json()
        
        self.assertDictEqual(tenant_json, {
            'id': None,  # ID will be assigned after the database commit
            'username': "alice_smith",
            'email': "alice_smith@example.com",
            'apartment_id': apartment.id,
        })

    def test_get_tenant_reviews(self):
        """Test retrieving all reviews written by a tenant."""
        apartment = Apartment(title="Big Apartment", description="Spacious apartment", location="321 Oak St", price=1500.00, lease_code="11223")
        db.session.add(apartment)
        db.session.commit()

        tenant = create_tenant("bob_jones", "bob_jones@example.com", "bobpass", "11223")
        
        # Assuming a Review model exists, we add a review here
        review = Review(tenant_id=tenant.id, apartment_id=apartment.id, content="Great place to live!", rating=5)
        db.session.add(review)
        db.session.commit()

        reviews = get_tenant_reviews(tenant.id)
        
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['content'], "Great place to live!")

    def test_get_all_tenants_json(self):
        """Test getting all tenants as JSON."""
        tenant1 = create_tenant("chris_lee", "chris_lee@example.com", "chrispass", "12345")
        tenant2 = create_tenant("diana_king", "diana_king@example.com", "dianapass", "98765")
        
        tenants_json = get_all_tenants_json()
        
        # Verify that the JSON representation contains the tenants' data
        self.assertEqual(len(tenants_json), 2)
        self.assertEqual(tenants_json[0]['username'], "chris_lee")
        self.assertEqual(tenants_json[1]['username'], "diana_king")
'''
'''
   #Unit Tests for Apartment Model and Controller


from App.constants import LOCATIONS  # Assuming LOCATIONS is imported here

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

    def test_update_apartment_amenities(self):
        """Test updating apartment amenities."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        updated_apartment = update_apartment_amenities(
            apartment.id, 
            ["Pool", "Gym"]
        )
        self.assertEqual(updated_apartment.amenities, ["Pool", "Gym"])

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
        result = delete_apartment(apartment.id)
        self.assertTrue(result)
        deleted_apartment = Apartment.query.get(apartment.id)
        self.assertIsNone(deleted_apartment)

    def test_verify_tenant(self):
        """Test tenant verification."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        lease_code = apartment.lease_code
        result = verify_tenant(self.tenant.id, lease_code)
        self.assertEqual(result['message'], "Tenant verified successfully.")

    def test_search_apartments(self):
        """Test searching apartments."""
        
        apartment1 = create_apartment(
            title="Test Apartment 1", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use a location from LOCATIONS list
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        apartment2 = create_apartment(
            title="Test Apartment 2", 
            description="Test Description", 
            location=LOCATIONS[1],  # Use a different location from LOCATIONS list
            price=1200.0, 
            landlord_id=self.landlord.id,
            amenities=["Gym"]
        )
        filters = {'location': LOCATIONS[0], 'amenities': ['WiFi']}
        results = search_apartments(filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Test Apartment 1")

    def test_get_reviews_for_apartment(self):
        """Test getting reviews for an apartment."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        review = Review(
            content="Great apartment!",
            rating=5,
            apartment_id=apartment.id,
            tenant_id=self.tenant.id
        )
        db.session.add(review)
        db.session.commit()
        reviews = get_reviews_for_apartment(apartment.id)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['content'], "Great apartment!")

    def test_get_all_tenants_of_apartment(self):
        """Test getting all tenants of an apartment."""
        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=self.landlord.id,
            amenities=["WiFi"]
        )
        review = Review(
            content="Great apartment!",
            rating=5,
            apartment_id=apartment.id,
            tenant_id=self.tenant.id
        )
        db.session.add(review)
        db.session.commit()
        tenants = get_all_tenants_of_apartment(apartment.id)
        self.assertEqual(len(tenants), 1)
        self.assertEqual(tenants[0]['username'], "tenant1")
'''
'''
   #Unit Tests for Review Model and Controller

class ReviewModelTestCase(unittest.TestCase):
    def setUp(self):
        # Setup app and database for testing
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Add test data (Landlord, Tenant, Apartment)
        self.landlord = Landlord(name='Test Landlord', email='landlord@test.com', password='password')
        self.tenant = Tenant(name='Test Tenant', email='tenant@test.com', password='password')
        self.apartment = Apartment(title='Test Apartment', description='Nice apartment', location='NYC', price=1000, landlord_id=1, amenities=[AMENITIES[0], AMENITIES[1]])
        
        db.session.add(self.landlord)
        db.session.add(self.tenant)
        db.session.add(self.apartment)
        db.session.commit()

    def tearDown(self):
        # Drop all tables after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_review(self):
        # Test creating a valid review
        review = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=4, comment="Great place!")
        db.session.add(review)
        db.session.commit()

        # Fetch the review from the database
        fetched_review = Review.query.get(review.id)
        self.assertEqual(fetched_review.comment, "Great place!")
        self.assertEqual(fetched_review.rating, 4)
        self.assertEqual(fetched_review.tenant_id, self.tenant.id)
        self.assertEqual(fetched_review.apartment_id, self.apartment.id)

    def test_get_reviews(self):
        # Create reviews
        review1 = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=4, comment="Great place!")
        review2 = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=5, comment="Awesome stay!")
        db.session.add(review1)
        db.session.add(review2)
        db.session.commit()

        # Get reviews for the apartment
        reviews = Review.query.filter_by(apartment_id=self.apartment.id).all()
        self.assertEqual(len(reviews), 2)

        review_json = [review.get_json() for review in reviews]
        self.assertEqual(review_json[0]["comment"], "Great place!")
        self.assertEqual(review_json[1]["rating"], 5)

    def test_update_review(self):
        # Create a review
        review = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=3, comment="Needs improvement.")
        db.session.add(review)
        db.session.commit()

        # Update the review
        updated_review = Review.query.get(review.id)
        updated_review.rating = 4
        updated_review.comment = "Better now."
        db.session.commit()

        # Fetch and check updated review
        updated_review = Review.query.get(review.id)
        self.assertEqual(updated_review.rating, 4)
        self.assertEqual(updated_review.comment, "Better now.")

    def test_delete_review(self):
        # Create a review
        review = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=3, comment="Needs improvement.")
        db.session.add(review)
        db.session.commit()

        # Delete the review
        db.session.delete(review)
        db.session.commit()

        # Check if review is deleted
        deleted_review = Review.query.get(review.id)
        self.assertIsNone(deleted_review)

    def test_create_review_with_invalid_rating(self):
        # Try to create a review with an invalid rating
        review = Review(tenant_id=self.tenant.id, apartment_id=self.apartment.id, rating=6, comment="Great place!")
        db.session.add(review)
        db.session.commit()

        # Check if review is not created
        review = Review.query.get(review.id)
        self.assertIsNone(review)

    def test_create_review_without_tenant_or_apartment(self):
        # Create review with non-existing tenant or apartment
        review = Review(tenant_id=9999, apartment_id=9999, rating=4, comment="Invalid")
        db.session.add(review)
        db.session.commit()

        # Check if review was created
        review = Review.query.get(review.id)
        self.assertIsNone(review)
'''
'''
   #Complex Tests to Ensure Foolproof Functionality


class ComplexLandlordTests(unittest.TestCase):

    def test_create_apartment_for_non_existent_landlord(self):
        """Test creating an apartment for a non-existent landlord."""
        try:
            add_apartment(999, "Luxury Apartment", "A high-end place", "101 High St", 2000.00, ["Spa", "Gym"])
            self.fail("Expected an error when creating an apartment for a non-existent landlord")
        except Exception as e:
            self.assertEqual(str(e), "Landlord not found")

    def test_create_landlord_with_existing_email(self):
        """Test creating a landlord with an already existing email."""
        create_landlord("george", "george@example.com", "georgepass")
        try:
            create_landlord("henry", "george@example.com", "henrypass")
            self.fail("Expected an error when creating a landlord with an existing email")
        except Exception as e:
            self.assertEqual(str(e), "Email already exists")

    def test_add_apartment_with_missing_fields(self):
        """Test adding an apartment with missing required fields."""
        landlord = create_landlord("jane", "jane@example.com", "janepass")
        try:
            add_apartment(landlord.id, "", "Missing title", "202 Maple St", 1400.00, [])
            self.fail("Expected an error when adding an apartment with missing title")
        except Exception as e:
            self.assertEqual(str(e), "Title is required")
'''
'''
   #Complex Tests to Ensure Foolproof Functionality


class ComplexTenantTests(unittest.TestCase):

    def test_create_tenant_with_existing_email(self):
        """Test creating a tenant with an already existing email."""
        apartment = Apartment(title="Cosy Home", description="Nice place", location="456 Oak St", price=1200.00, lease_code="54321")
        db.session.add(apartment)
        db.session.commit()

        create_tenant("emily_ross", "emily_ross@example.com", "emilypass", "54321")

        try:
            create_tenant("emily_smith", "emily_ross@example.com", "emilysmithpass", "54321")
            self.fail("Expected an error when creating a tenant with an existing email")
        except Exception as e:
            self.assertEqual(str(e), "Email already exists")

    def test_create_tenant_without_lease_code(self):
        """Test that creating a tenant without a lease code raises an error."""
        try:
            create_tenant("george_white", "george_white@example.com", "georgepass", "")
            self.fail("Expected an error when creating a tenant without a lease code")
        except ValueError as e:
            self.assertEqual(str(e), "Lease code cannot be empty")

    def test_create_tenant_invalid_password(self):
        """Test creating a tenant with a weak password."""
        apartment = Apartment(title="Small Unit", description="Basic apartment", location="777 Birch St", price=800.00, lease_code="77788")
        db.session.add(apartment)
        db.session.commit()

        try:
            create_tenant("hannah_blue", "hannah_blue@example.com", "short", "77788")
            self.fail("Expected an error when creating a tenant with a weak password")
        except ValueError as e:
            self.assertEqual(str(e), "Password is too short")'
'''