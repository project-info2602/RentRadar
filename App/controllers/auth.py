from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from App.models import Landlord, Tenant

def login(username, password, role):
    # Check if user is a Landlord or Tenant
    if role == "landlord":
        user = Landlord.query.filter_by(username=username).first()
    else:
        user = Tenant.query.filter_by(username=username).first()

    if user and user.check_password(password):
        return create_access_token(identity=username)
    return None


def setup_jwt(app):
    jwt = JWTManager(app)

    # configure's flask jwt to resolve get_current_identity() to the corresponding user's ID
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        landlord = Landlord.query.filter_by(username=identity).one_or_none()
        if landlord:
            return landlord.id
        tenant = Tenant.query.filter_by(username=identity).one_or_none()
        if tenant:
            return tenant.id
        return None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # First look for the user as a Landlord
        landlord = Landlord.query.get(identity)
        if landlord:
            return landlord
        # If not found, look for the user as a Tenant
        tenant = Tenant.query.get(identity)
        if tenant:
            return tenant
        return None

    return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            current_user = Landlord.query.get(user_id)
            if not current_user:
                current_user = Tenant.query.get(user_id)
            is_authenticated = True
        except Exception as e:
            print(e)
            is_authenticated = False
            current_user = None
        return dict(is_authenticated=is_authenticated, current_user=current_user)
