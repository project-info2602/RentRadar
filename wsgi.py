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
    initialize
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
Review Commands
'''

review_cli = AppGroup('review', help='Review object commands')  # Review commands group

@review_cli.command("create", help="Creates a review for an apartment")
@click.argument("tenant_id", type=int)  # Updated from user_id to tenant_id
@click.argument("apartment_id", type=int)
@click.argument("rating", type=int)
@click.argument("comment")
def create_review_command(tenant_id, apartment_id, rating, comment):
    try:
        response, status_code = create_review(tenant_id, apartment_id, rating, comment)
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

@test.command("landlord", help="Run Landlord tests")
@click.argument("type", default="all")
def landlord_tests_command(type):
    try:
        if type == "unit":
            sys.exit(pytest.main(["-k", "LandlordUnitTests"]))
        elif type == "int":
            sys.exit(pytest.main(["-k", "LandlordIntegrationTests"]))
        else:
            sys.exit(pytest.main(["-k", "App"]))
    except Exception as e:
        print(f"Error running tests: {e}")
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