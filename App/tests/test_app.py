import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Apartment, Amenity, Review
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user,
    create_apartment,
    get_apartment,
    create_review,
    link_apartment_to_amenity,
    create_amenity,
    get_all_amenities,
    search_apartments
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests for User Model and Controller
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        # Create a new user with given parameters
        user = User("bob", "bob@example.com", "bobpass", "tenant")
        
        # Check if the user attributes are correctly assigned
        self.assertEqual(user.username, "bob")
        self.assertEqual(user.role, "tenant")
        self.assertEqual(user.email, "bob@example.com")

    def test_get_json(self):
        # Create a new user
        user = User("bob", "bob@example.com", "bobpass", "tenant")
        
        # Get the JSON representation of the user
        user_json = user.get_json()

        # Check if the returned JSON is as expected
        self.assertDictEqual(user_json, {
            "id": None,  # Assuming the user ID is None until it's saved in the DB
            "username": "bob",
            "email": "bob@example.com",
            "role": "tenant"
        })
    
    def test_check_password(self):
        password = "mypass"
        
        # Create a user with a plain-text password
        user = User("bob", "bob@example.com", password, "tenant")
        
        # Check if the user can verify the correct password
        self.assertTrue(user.check_password(password))
        
        # Check if the user fails with an incorrect password
        self.assertFalse(user.check_password("wrongpassword"))


'''
   Unit Tests for Apartment Model and Controller
'''
class ApartmentUnitTests(unittest.TestCase):

    def test_create_apartment(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        apartment = Apartment(title="Cozy Apartment", description="A comfortable place", location="123 Main St", price=1000.00, landlord_id=user.id)
        
        # Verifying the attributes of the apartment
        self.assertEqual(apartment.title, "Cozy Apartment")
        self.assertEqual(apartment.location, "123 Main St")
        self.assertEqual(apartment.price, 1000.00)

    def test_apartment_to_json(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        apartment = Apartment(title="Spacious Apartment", description="A spacious place", location="456 Oak St", price=1200.00, landlord_id=user.id)
        
        # Convert apartment to JSON and check if it matches the expected structure
        apartment_json = apartment.get_json()
        self.assertDictEqual(apartment_json, {
            "id": None, 
            "title": "Spacious Apartment", 
            "description": "A spacious place", 
            "location": "456 Oak St", 
            "price": 1200.00, 
            "landlord_id": user.id,
            "reviews": [],  # Assuming no reviews initially
            "amenities": []  # Assuming no amenities linked initially
        })

    def test_search_apartments_location(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        create_apartment("Cozy Apartment", "A comfortable place", "123 Main St", 1000.00, user.id)
        create_apartment("Luxury Apartment", "A luxury apartment", "456 Oak St", 2000.00, user.id)
        
        filters = {"location": "Oak"}
        apartments = search_apartments(filters)
        
        # Verifying that the search returns the expected results
        self.assertEqual(len(apartments), 1)
        self.assertEqual(apartments[0].title, "Luxury Apartment")

    def test_search_apartments_price(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        create_apartment("Cozy Apartment", "A comfortable place", "123 Main St", 1000.00, user.id)
        create_apartment("Luxury Apartment", "A luxury apartment", "456 Oak St", 2000.00, user.id)
        
        filters = {"price": 1500}
        apartments = search_apartments(filters)
        
        # Verifying that the search filters for price return the expected results
        self.assertEqual(len(apartments), 1)
        self.assertEqual(apartments[0].price, 1000.00)

    def test_search_apartments_amenities(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        create_apartment("Cozy Apartment", "A comfortable place", "123 Main St", 1000.00, user.id)
        
        gym = create_amenity("Gym")
        pool = create_amenity("Swimming Pool")
        apartment = create_apartment("Spacious Apartment", "A spacious place", "456 Oak St", 1200.00, user.id)
        
        # Linking amenities
        link_apartment_to_amenity(apartment.id, gym.id)
        link_apartment_to_amenity(apartment.id, pool.id)

        filters = {"amenities": "Gym"}
        apartments = search_apartments(filters)

        # Verifying the apartment has the correct amenities linked
        self.assertEqual(len(apartments), 1)
        self.assertIn(gym.name, [amenity.name for amenity in apartments[0].amenities])

    def test_search_apartments_multiple_filters(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        create_apartment("Cozy Apartment", "A comfortable place", "123 Main St", 1000.00, user.id)
        create_apartment("Luxury Apartment", "A luxury apartment", "456 Oak St", 2000.00, user.id)
        
        filters = {"location": "Oak", "price": 1500}
        apartments = search_apartments(filters)
        
        # Verifying the results for multiple filters
        self.assertEqual(len(apartments), 1)
        self.assertEqual(apartments[0].price, 1000.00)
        self.assertEqual(apartments[0].location, "456 Oak St")



'''
   Unit Tests for Review Model and Controller
'''
class ReviewUnitTests(unittest.TestCase):

    def test_create_review(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        apartment = Apartment("Cozy Apartment", "A comfortable place", "123 Main St", 1000.00, user.id)
        review = Review(user.id, apartment.id, 5, "Great place to live!")
        assert review.rating == 5
        assert review.comment == "Great place to live!"

    def test_review_to_json(self):
        user = User("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        apartment = Apartment("Spacious Apartment", "A spacious place", "456 Oak St", 1200.00, user.id)
        review = Review(user.id, apartment.id, 4, "Good apartment")
        review_json = review.to_json()
        self.assertDictEqual(review_json, {"id": None, "user_id": user.id, "apartment_id": apartment.id, "rating": 4, "comment": "Good apartment"})


'''
   Complex Tests to Ensure Foolproof Functionality
'''
class ComplexTests(unittest.TestCase):

    def test_create_multiple_users_and_apartments(self):
        user_1 = create_user("alice", "alice@example.com", "alicepass", "tenant")  # Updated parameters
        user_2 = create_user("bob", "bob@example.com", "bobpass", "landlord")  # Updated parameters
        
        apartment_1 = create_apartment("Apartment 1", "Nice place", "123 Maple St", 1500.00, user_2.id)
        apartment_2 = create_apartment("Apartment 2", "Cozy place", "456 Oak St", 1000.00, user_2.id)

        assert apartment_1.title == "Apartment 1"
        assert apartment_2.title == "Apartment 2"
        
        filters = {"price": 1200}
        apartments = search_apartments(filters)
        assert len(apartments) == 1
        assert apartments[0].title == "Apartment 2"
    
    def test_create_review_for_non_existent_apartment(self):
        user = create_user("charlie", "charlie@example.com", "charliepass", "tenant")  # Updated parameters
        try:
            create_review(user.id, 999, 5, "Amazing place!")  # Non-existent apartment ID
            assert False, "Expected an error when creating a review for a non-existent apartment"
        except Exception as e:
            assert str(e) == "Apartment not found"

    def test_create_apartment_for_non_existent_user(self):
        try:
            create_apartment("Apartment 3", "Another nice place", "789 Pine St", 1200.00, 999)  # Non-existent user ID
            assert False, "Expected an error when creating an apartment for a non-existent user"
        except Exception as e:
            assert str(e) == "User not found"

    def test_create_user_with_existing_email(self):
        create_user("bob", "bob@example.com", "bobpass", "tenant")  # Updated parameters
        try:
            create_user("bob2", "bob@example.com", "bobpass", "tenant")  # Duplicate email
            assert False, "Expected an error when creating a user with an existing email"
        except Exception as e:
            assert str(e) == "Email already exists"

    def test_create_apartment_with_missing_fields(self):
        user = create_user("dave", "dave@example.com", "davepass", "landlord")  # Updated parameters
        try:
            create_apartment("", "Missing title", "123 Elm St", 1500.00, user.id)  # Missing title
            assert False, "Expected an error when creating an apartment with missing fields"
        except Exception as e:
            assert str(e) == "Title is required"

