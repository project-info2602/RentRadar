import click, pytest, sys
from flask import Flask
from flask.cli import AppGroup

from App.database import db, get_migrate
from App.constants import AMENITIES, LOCATIONS
from App.models import Landlord, Tenant, Apartment, Review
from App.main import create_app
from App.controllers import (
    create_landlord, 
    create_tenant, 
    get_all_landlords_json, 
    get_all_landlords,
    get_all_tenants_json, 
    get_all_tenants, 
    create_apartment, 
    get_apartments, 
    create_review, 
    get_reviews, 
    initialize,
    update_apartment,
    delete_apartment,
    search_apartments,
    get_reviews_for_apartment
)

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
Landlord Commands
'''

landlord_cli = AppGroup('landlord', help='Landlord object commands')  # Landlord commands group

@landlord_cli.command("create", help="Creates a landlord")
@click.argument("username", default="rob")
@click.argument("email", default="rob@example.com")
@click.argument("password", default="robpass")
def create_landlord_command(username, email, password):
    try:
        landlord = create_landlord(username, email, password)
        if isinstance(landlord, Landlord):  # Check if creation was successful
            print(f'{username} created successfully!')
        else:
            print(f"Error: {landlord['message']}")  # Error message if creation failed
    except Exception as e:
        print(f"Error creating landlord: {e}")

@landlord_cli.command("list", help="Lists landlords in the database")
@click.argument("format", default="string")
def list_landlord_command(format):
    try:
        if format == 'string':
            landlords = get_all_landlords()
            if landlords:
                for landlord in landlords:
                    print(f"{landlord.username} ({landlord.email})")
            else:
                print("No landlords found.")
        else:
            landlords_json = get_all_landlords_json()
            if landlords_json:
                print(landlords_json)
            else:
                print("No landlords found.")
    except Exception as e:
        print(f"Error fetching landlords: {e}")

app.cli.add_command(landlord_cli)  # Add landlord commands group to the app

'''
Tenant Commands
'''

tenant_cli = AppGroup('tenant', help='Tenant object commands')  # Tenant commands group

@tenant_cli.command("create", help="Creates a tenant")
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.argument("lease_code")  # Tenant creation now requires lease code
def create_tenant_command(username, email, password, lease_code):
    try:
        tenant = create_tenant(username, email, password, lease_code)
        if isinstance(tenant, Tenant):  # Check if creation was successful
            print(f'{username} created successfully!')
        else:
            print(f"Error: {tenant['message']}")  # Error message if creation failed
    except Exception as e:
        print(f"Error creating tenant: {e}")

@tenant_cli.command("list", help="Lists tenants in the database")
@click.argument("format", default="string")
def list_tenant_command(format):
    try:
        if format == 'string':
            tenants = get_all_tenants()
            if tenants:
                for tenant in tenants:
                    print(f"{tenant.username} ({tenant.email})")
            else:
                print("No tenants found.")
        else:
            tenants_json = get_all_tenants_json()
            if tenants_json:
                print(tenants_json)
            else:
                print("No tenants found.")
    except Exception as e:
        print(f"Error fetching tenants: {e}")

app.cli.add_command(tenant_cli)  # Add tenant commands group to the app

'''
Apartment Commands
'''

apartment_cli = AppGroup('apartment', help='Apartment object commands')  # Apartment commands group

@apartment_cli.command("create", help="Creates an apartment")
@click.option("--title", default="Cozy Studio")
@click.option("--description", default="A cozy studio in the city center")
@click.option("--location", default=LOCATIONS[0])
@click.option("--price", type=float, default=1500)
@click.option("--landlord_id", type=int, default=1)
def create_apartment_command(title, description, location, price, landlord_id):
    try:
        if location not in LOCATIONS:
            print(f"Error: '{location}' is not a valid location. Choose from: {', '.join(LOCATIONS)}")
            return

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

@apartment_cli.command("update", help="Updates an apartment (except location)")
@click.argument("apartment_id", type=int)
@click.option("--title", default=None, help="New title")
@click.option("--description", default=None, help="New description")
@click.option("--price", type=float, default=None, help="New price")
@click.option("--amenities", multiple=True, help="New amenities (must be valid)")
def update_apartment_command(apartment_id, title, description, price, amenities):
    try:
        amenities_list = list(amenities) if amenities else None

        if amenities_list:
            invalid = [a for a in amenities_list if a not in AMENITIES]
            if invalid:
                print(f"Invalid amenities found: {', '.join(invalid)}")
                print(f"Allowed amenities are: {', '.join(AMENITIES)}")
                return

        updated = update_apartment(apartment_id, title, description, price, amenities_list)
        if updated:
            print(f"Apt #{apartment_id} updated successfully.")
        else:
            print("Apartment not found.")
    except Exception as e:
        print(f"Error updating apartment: {e}")


@apartment_cli.command("delete", help="Deletes an apartment")
@click.argument("apartment_id", type=int)
def delete_apartment_command(apartment_id):
    try:
        result = delete_apartment(apartment_id)
        if result:
            print(f"Apt #{apartment_id} deleted successfully.")
        else:
            print("Apartment not found.")
    except Exception as e:
        print(f"Error deleting apartment: {e}")

@apartment_cli.command("search", help="Search apartments by location and amenities")
@click.option("--location", default=None)
@click.option("--amenities", multiple=True)
def search_apartment_command(location, amenities):
    try:
        filters = {}

        if location:
            if location not in LOCATIONS:
                print(f"Error: '{location}' is not a valid location. Choose from: {', '.join(LOCATIONS)}")
                return
            filters['location'] = location

        if amenities:
            invalid = [a for a in amenities if a not in AMENITIES]
            if invalid:
                print(f"Error: Invalid amenities: {', '.join(invalid)}. Allowed: {', '.join(AMENITIES)}")
                return
            filters['amenities'] = list(amenities)

        results = search_apartments(filters)
        if results:
            for apt in results:
                print(f"{apt.id}: {apt.title} - {apt.location} - ${apt.price} | Amenities: {', '.join(apt.amenities)}")
        else:
            print("No apartments found.")
    except Exception as e:
        print(f"Error searching apartments: {e}")


@apartment_cli.command("reviews", help="List reviews for an apartment")
@click.argument("apartment_id", type=int)
def apartment_reviews_command(apartment_id):
    try:
        reviews = get_reviews_for_apartment(apartment_id)  # Assuming this returns a list of dictionaries
        if reviews:
            for review in reviews:
                # Print the review information using the correct keys
                print(f"Rating: {review.get('rating')} | Comment: {review.get('comment')} (Tenant #{review.get('tenant_id')})")
        else:
            print("No reviews found.")
    except Exception as e:
        print(f"Error retrieving reviews: {e}")

app.cli.add_command(apartment_cli)

'''
Review Commands
'''

review_cli = AppGroup('review', help='Review object commands')

@review_cli.command("create", help="Creates a review for an apartment")
@click.argument("tenant_id", type=int)
@click.argument("apartment_id", type=int)
@click.argument("rating", type=int)
@click.argument("comment")
def create_review_command(tenant_id, apartment_id, rating, comment):
    try:
        response = create_review(tenant_id, apartment_id, rating, comment)
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

app.cli.add_command(review_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands')

@test.command("landlord", help="Run Landlord tests")
@click.argument("type", default="all")
def landlord_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "LandlordUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "LandlordIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "Landlord"]))
    except Exception as e:
        print(f"Error running landlord tests: {e}")
        sys.exit(1)

@test.command("tenant", help="Run Tenant tests")
@click.argument("type", default="all")
def tenant_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "TenantUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "TenantIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "Tenant"]))
    except Exception as e:
        print(f"Error running tenant tests: {e}")
        sys.exit(1)

@test.command("apartment", help="Run Apartment tests")
@click.argument("type", default="all")
def apartment_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "ApartmentUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "ApartmentIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "Apartment"]))
    except Exception as e:
        print(f"Error running apartment tests: {e}")
        sys.exit(1)

@test.command("review", help="Run Review tests")
@click.argument("type", default="all")
def review_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "ReviewUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "ReviewIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "Review"]))
    except Exception as e:
        print(f"Error running review tests: {e}")
        sys.exit(1)

@app.cli.command("test", help="Run all tests")
def run_tests():
    try:
        sys.exit(pytest.main(["-k", "App"]))
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

app.cli.add_command(test)
