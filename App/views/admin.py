from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask import flash, redirect, url_for, request
from flask_jwt_extended import jwt_required, current_user

from App.models import Landlord, Tenant, Apartment, Review
from App.database import db

class SecureModelView(ModelView):
    def is_accessible(self):
        try:
            jwt_required()(lambda: None)()
            return current_user is not None
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be logged in to access the admin panel.")
        return redirect(url_for('index_views.index_page', next=request.url))


def setup_admin(app):
    admin = Admin(app, name='RentRadar Admin', template_mode='bootstrap3')

    # Register your models with admin interface
    admin.add_view(SecureModelView(Landlord, db.session))
    admin.add_view(SecureModelView(Tenant, db.session))
    admin.add_view(SecureModelView(Apartment, db.session))
    admin.add_view(SecureModelView(Review, db.session))
