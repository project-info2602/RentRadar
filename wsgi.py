import click, pytest, sys
from flask import Flask
from flask.cli import AppGroup

from App.database import db, get_migrate
from App.models import User, Apartment, Amenity, Review
from App.main import create_app
from App.controllers import create_user, get_all_users_json, get_all_users, create_apartment, get_apartments, create_amenity, get_all_amenities, create_review, get_reviews, initialize

# Create app and migrate
app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    try:
        initialize()
        print('Database initialized')
    except Exception as e:
        print(f"Error initializing database: {e}")


'''
User Commands
'''

user_cli = AppGroup('user', help='User object commands')  # User commands group

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("email", default="rob@example.com")
@click.argument("password", default="robpass")
@click.argument("role", default="tenant")
def create_user_command(username, email, password, role):
    try:
        user = create_user(username, email, password, role)
        if isinstance(user, User):  # Check if user creation was successful
            print(f'{username} created successfully!')
        else:
            print(f"Error: {user['message']}")  # Error message if creation failed
    except Exception as e:
        print(f"Error creating user: {e}")


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    try:
        if format == 'string':
            users = get_all_users()
            if users:
                for user in users:
                    print(f"{user.username} ({user.email}) - {user.role}")
            else:
                print("No users found.")
        else:
            users_json = get_all_users_json()
            if users_json:
                print(users_json)
            else:
                print("No users found.")
    except Exception as e:
        print(f"Error fetching users: {e}")

app.cli.add_command(user_cli)  # Add the user commands group to the app


'''
Apartment Commands
'''

apartment_cli = AppGroup('apartment', help='Apartment object commands')  # Apartment commands group

@apartment_cli.command("create", help="Creates an apartment")
@click.argument("title", default="Cozy Studio")
@click.argument("description", default="A cozy studio in the city center")
@click.argument("location", default="New York")
@click.argument("price", default=1500)
@click.argument("landlord_id", default=1)
def create_apartment_command(title, description, location, price, landlord_id):
    try:
        apartment = create_apartment(title, description, location, price, landlord_id)
        print(f"Apartment '{apartment.title}' created successfully!")
    except Exception as e:
        print(f"Error creating apartment: {e}")

@apartment_cli.command("list", help="Lists apartments in the database")
def list_apartment_command():
    try:
        apartments = get_apartments()
        if apartments:
            for apartment in apartments:
                print(f"{apartment.title} - {apartment.location} - ${apartment.price}")
        else:
            print("No apartments found.")
    except Exception as e:
        print(f"Error fetching apartments: {e}")

app.cli.add_command(apartment_cli)  # Add the apartment commands group to the app


'''
Amenity Commands
'''

amenity_cli = AppGroup('amenity', help='Amenity object commands')  # Amenity commands group

@amenity_cli.command("create", help="Creates an amenity")
@click.argument("name", default="Swimming Pool")
def create_amenity_command(name):
    try:
        amenity = create_amenity(name)
        print(f"Amenity '{amenity.name}' created successfully!")
    except Exception as e:
        print(f"Error creating amenity: {e}")

@amenity_cli.command("list", help="Lists amenities in the database")
def list_amenity_command():
    try:
        amenities = get_all_amenities()
        if amenities:
            for amenity in amenities:
                print(f"{amenity.name}")
        else:
            print("No amenities found.")
    except Exception as e:
        print(f"Error fetching amenities: {e}")

app.cli.add_command(amenity_cli)  # Add the amenity commands group to the app


'''
Review Commands
'''

review_cli = AppGroup('review', help='Review object commands')  # Review commands group

@review_cli.command("create", help="Creates a review for an apartment")
@click.argument("user_id", type=int)
@click.argument("apartment_id", type=int)
@click.argument("rating", type=int)
@click.argument("comment")
def create_review_command(user_id, apartment_id, rating, comment):
    try:
        response, status_code = create_review(user_id, apartment_id, rating, comment)
        print(response['message'])
    except Exception as e:
        print(f"Error creating review: {e}")


@review_cli.command("list", help="Lists reviews for an apartment")
@click.argument("apartment_id", default=1)
def list_review_command(apartment_id):
    try:
        reviews = get_reviews(apartment_id)
        if reviews:
            for review in reviews:
                print(f"Rating: {review.rating}, Comment: {review.comment}")
        else:
            print("No reviews found.")
    except Exception as e:
        print(f"Error fetching reviews: {e}")

app.cli.add_command(review_cli)  # Add the review commands group to the app


'''
Test Commands
'''

test = AppGroup('test', help='Testing commands')

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "UserUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "App"]))
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

@app.cli.command("test", help="Run all tests")
def run_tests():
    try:
        sys.exit(pytest.main(["-k", "App"]))
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

app.cli.add_command(test)  # Add the test commands group to the app
