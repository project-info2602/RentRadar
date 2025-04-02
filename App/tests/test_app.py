import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass", "tenant")  # Added role
        assert user.username == "bob"
        assert user.role == "tenant"

    def test_get_json(self):
        user = User("bob", "bobpass", "tenant")  # Added role
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id": None, "username": "bob", "role": "tenant"})  # Added role field
    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password, "tenant")  # Added role
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password, "tenant")  # Added role
        assert user.check_password(password)

'''
    Integration Tests
'''

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


def test_authenticate():
    user = create_user("bob", "bobpass", "tenant")  # Added role
    db.session.commit()  # Commit so login() works
    assert login("bob", "bobpass") is not None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_user(self):
        user = create_user("rick", "bobpass", "landlord")  # Added role
        db.session.commit()  # Commit to database
        assert user.username == "rick"
        assert user.role == "landlord"

    def test_get_all_users_json(self):
        users_json = get_all_users_json()
        expected_users = [
            {"id": 1, "username": "bob", "role": "tenant"},
            {"id": 2, "username": "rick", "role": "landlord"}
        ]  # Ensure role is included
        self.assertListEqual(expected_users, users_json)

    def test_update_user(self):
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"
