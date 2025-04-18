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
    create_apartment, 
    update_apartment, 
    delete_apartment, 
    search_apartments, 
    get_reviews_for_apartment, 
    get_all_tenants_of_apartment,
    get_apartment_via_leasecode,    #just added to test
    is_tenant_verified,                  #just added to test
    create_review,
    get_reviews,
    update_review,
    delete_review
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
        
        tenant_json = tenant.get_json()
        
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

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

    def test_create_apartment(self):
        """Test apartment creation."""
        landlord = create_landlord("greg", "greg@example.com", "gregpass")

        result = create_apartment(
            landlord_id=landlord.id,
            title="Test Apartment",
            description="Test Description",
            location=LOCATIONS[0],
            price=1000.0,
            amenities= [AMENITIES[0], AMENITIES[2]]
        )

        if isinstance(result, tuple):
            self.fail(f"Apartment creation failed with error: {result[0]}")

        apartment = result

        self.assertIsNotNone(apartment.id)  # Ensure the apartment has an ID
        self.assertEqual(apartment.title, "Test Apartment")  # Check the apartment title
        self.assertEqual(apartment.description, "Test Description")
        self.assertEqual(apartment.location, LOCATIONS[0])  # Ensure the location is correct
        self.assertEqual(apartment.price, 1000.0)
        self.assertEqual(apartment.amenities, [AMENITIES[0], AMENITIES[2]])  # Verify amenities

    def test_update_apartment(self):
        
        landlord = create_landlord("greg", "greg@example.com", "gregpass")

        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=landlord.id,
            amenities=[AMENITIES[0]]
        )

    # Updating the apartment amenities
        updated_apartment = update_apartment(
            apartment.id, 
            title="Updated Test Apartment", 
            description="Updated Test Description", 
            price=1200.0, 
            amenities_list=[AMENITIES[1], AMENITIES[2]]
        )

        # Check if the apartment is updated correctly
        self.assertEqual(updated_apartment.title, "Updated Test Apartment")
        self.assertEqual(updated_apartment.description, "Updated Test Description")
        self.assertEqual(updated_apartment.price, 1200.0)  # Verify updated price
        self.assertEqual(updated_apartment.amenities, [AMENITIES[1], AMENITIES[2]])  # Verify amenities updated


    def test_delete_apartment(self):
        """Test deleting an apartment."""
        landlord = create_landlord("greg", "greg@example.com", "gregpass")

        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0],  # Use the first location from LOCATIONS
            price=1000.0, 
            landlord_id=landlord.id,
            amenities=[AMENITIES[0], AMENITIES[2], AMENITIES[3]]
        )
        apartment_id = apartment.id
        delete_apartment(apartment_id)
        apartment = Apartment.query.get(apartment_id)
        self.assertIsNone(apartment)  # Should be None since it was deleted

    def test_search_apartments(self):
        """Test searching for apartments."""
        landlord = create_landlord("greg", "greg@example.com", "gregpass")

        apartment = create_apartment(
            title="Test Apartment", 
            description="Test Description", 
            location=LOCATIONS[0], 
            price=1000.0, 
            landlord_id=landlord.id,
            amenities=[AMENITIES[0], AMENITIES[2], AMENITIES[3]]
        )
        apartments = search_apartments({
            "location": LOCATIONS[0],
            "amenities": [AMENITIES[0], AMENITIES[2], AMENITIES[3]]
        })

        self.assertEqual(len(apartments), 1)  # Should return 1 apartment
        self.assertEqual(apartments[0].title, "Test Apartment")

    def test_get_reviews_for_apartment(self):
        # Set up landlord, tenant, and apartment
        landlord = create_landlord("testlandlord", "landlord@test.com", "password")
        
        apartment = create_apartment(
            title="Sample Apartment",
            description="A test apartment",
            location=LOCATIONS[0],
            price=900.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[0]]
        )

        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment.lease_code)
        tenant2 = create_tenant("jimbo", "jimbo@test.com", "jimbopass", apartment.lease_code)
        

        # Add a review
        review1 = create_review(tenant1.id, apartment.id, rating=4, comment="Nice place")
        review2 = create_review(tenant2.id, apartment.id, rating=3, comment="Decent place")

        result = get_reviews_for_apartment(apartment.id)

        # Assert that the result is a list and contains both reviews
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # Should return 2 reviews
        self.assertEqual(result[0]['comment'], "Nice place")  # Check first review comment
        self.assertEqual(result[1]['comment'], "Decent place")  # Check second review comment

    def test_get_all_tenants_of_apartment(self):
        # Set up landlord, tenant, and apartment
        landlord = create_landlord("testlandlord2", "landlord2@test.com", "password")
    
        apartment = create_apartment(
            title="Another Apartment",
            description="Another test apartment",
            location=LOCATIONS[1],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )
    
        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment.lease_code)
        tenant2 = create_tenant("jimbo", "jimbo@test.com", "jimbopass", apartment.lease_code)
    
        # Link tenants to apartment through reviews
        review1 = create_review(tenant1.id, apartment.id, rating=4, comment="Nice place")
        review2 = create_review(tenant2.id, apartment.id, rating=3, comment="Decent place")

        # Call the function to get tenants for the apartment
        result = get_all_tenants_of_apartment(apartment.id)

        # Assert that the result is a list and contains both tenants
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # Should return 2 tenants
        self.assertEqual(result[0]['username'], "testtenant")  # Check first tenant's username
        self.assertEqual(result[1]['username'], "jimbo")  # Check second tenant's username

    def test_get_apartment_via_leasecode(self):
    
        landlord = Landlord(username="testlandlord", email="landlord@example.com", password="password")
        db.session.add(landlord)
        db.session.commit()

        apt = create_apartment(
            title="Test Apt",
            description="Nice place",
            location=LOCATIONS[0],
            price=1500,
            landlord_id=landlord.id,
            amenities=[AMENITIES[0], AMENITIES[1]]
        )

        db.session.refresh(apt)

        fetched = get_apartment_via_leasecode(apt.lease_code)

        assert fetched is not None
        assert isinstance(fetched, Apartment)
        assert fetched.id == apt.id
        assert fetched.lease_code == apt.lease_code

    def test_verify_tenant_success(self):

        landlord = create_landlord("landy", "landy@example.com", "securepass")

        apartment = create_apartment(
            title="Hilltop Retreat",
            description="Nice view, quiet area",
            location=LOCATIONS[0],
            price=1200,
            landlord_id=landlord.id,
            amenities=[AMENITIES[0], AMENITIES[1]]
        )

        tenant = create_tenant(
            username="tomtenant",
            email="tom@example.com",
            password="secure123",
            lease_code=apartment.lease_code
        )

        result = is_tenant_verified(tenant.id, apartment.lease_code)

        refreshed_apartment = Apartment.query.get(apartment.id)  # Refresh to reflect new relationships

        self.assertTrue(result)
        self.assertIn(tenant, refreshed_apartment.tenants)

    def test_verify_tenant_fail(self):
        landlord = create_landlord("landyfail", "landyfail@example.com", "securepass")

        apartment1 = create_apartment(
            title="Ocean View",
            description="Breezy and calm",
            location=LOCATIONS[0],
            price=1500,
            landlord_id=landlord.id,
            amenities=[AMENITIES[0]]
        )

        apartment2 = create_apartment(
            title="Mountain View",
            description="Breezy and calm",
            location=LOCATIONS[0],
            price=1500,
            landlord_id=landlord.id,
            amenities=[AMENITIES[0]]
        )

        tenant = create_tenant(
            username="failtenant",
            email="fail@example.com",
            password="secure123",
            lease_code=apartment1.lease_code
        )

        result = is_tenant_verified(tenant.id, apartment2.lease_code)

        refreshed_apartment = Apartment.query.get(apartment2.id)  # Refresh apartment2 state

        self.assertFalse(result)
        self.assertNotIn(tenant, refreshed_apartment.tenants)


class ReviewFunctionsTestCase(unittest.TestCase):
    
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

    def test_create_review(self):
        """Test creating a new review."""

        landlord = create_landlord("testlandlord2", "landlord2@test.com", "password")
    
        apartment1 = create_apartment(
            title="Another Apartment",
            description="Another test apartment",
            location=LOCATIONS[1],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )

        apartment2 = create_apartment(
            title="Another Apartment 1",
            description="Another test apartment",
            location=LOCATIONS[3],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )

        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment1.lease_code)

        review = create_review(tenant1.id, apartment1.id, 5, "Great place!")
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great place!")

        # Test invalid review (tenant not verified for the apartment)
        review_invalid = create_review(tenant1.id, apartment2.id, 4, "Nice place")
        self.assertIsNone(review_invalid)

    def test_get_reviews(self):
        """Test fetching all reviews for an apartment."""

        landlord = create_landlord("testlandlord2", "landlord2@test.com", "password")
    
        apartment = create_apartment(
            title="Another Apartment",
            description="Another test apartment",
            location=LOCATIONS[1],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )
    
        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment.lease_code)
        tenant2 = create_tenant("jimbo", "jimbo@test.com", "jimbopass", apartment.lease_code)

        create_review(tenant1.id, apartment.id, 5, "Great place!")
        create_review(tenant2.id, apartment.id, 4, "Nice place")

        reviews = get_reviews(apartment.id)
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]['comment'], "Great place!")
        self.assertEqual(reviews[1]['comment'], "Nice place")

    def test_update_review(self):
        """Test updating a review."""

        landlord = create_landlord("testlandlord2", "landlord2@test.com", "password")
    
        apartment = create_apartment(
            title="Another Apartment",
            description="Another test apartment",
            location=LOCATIONS[1],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )
    
        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment.lease_code)

        review = create_review(tenant1.id, apartment.id, 4, "Good place")
        updated_review = update_review(review.id, {'rating': 5, 'comment': "Great place!"})
        
        self.assertIsNotNone(updated_review)
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.comment, "Great place!")

        # Try updating a non-existent review
        result = update_review(9999, {'rating': 5, 'comment': "Does not exist"})
        self.assertIsNone(result)

    def test_delete_review(self):
        """Test deleting a review."""

        landlord = create_landlord("testlandlord2", "landlord2@test.com", "password")
    
        apartment = create_apartment(
            title="Another Apartment",
            description="Another test apartment",
            location=LOCATIONS[1],
            price=950.0,
            landlord_id=landlord.id,
            amenities=[AMENITIES[1]]
        )
    
        tenant1 = create_tenant("testtenant", "tenant@test.com", "password", apartment.lease_code)

        review = create_review(tenant1.id, apartment.id, 4, "Good place")
        result = delete_review(review.id)
        self.assertTrue(result)

        # Try deleting a non-existent review
        result = delete_review(9999)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()