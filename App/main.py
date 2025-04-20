from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, set_access_cookies, unset_jwt_cookies
from App.models import Landlord, Tenant, Apartment, Review
from App.database import db
from App.constants import AMENITIES, LOCATIONS
import os
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-jwt-key')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_NAME'] = 'access_token'
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    jwt = JWTManager(app)

    # Debug route to check all registered routes
    @app.route('/debug-routes')
    def debug_routes():
        return '<pre>' + '\n'.join([str(rule) for rule in app.url_map.iter_rules()]) + '</pre>'
    # Home and Auth Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                password = request.form.get('password')
                role = request.form.get('role')
                
                if not all([username, password, role]):
                    flash('All fields are required', 'danger')
                    return redirect(url_for('login'))

                user = None
                if role == 'landlord':
                    user = Landlord.query.filter_by(username=username).first()
                elif role == 'tenant':
                    user = Tenant.query.filter_by(username=username).first()
                else:
                    flash('Invalid role selected', 'danger')
                    return redirect(url_for('login'))

                if not user or not user.check_password(password):
                    flash('Invalid username or password', 'danger')
                    return redirect(url_for('login'))

                access_token = create_access_token(identity={
                    'id': user.id,
                    'role': role,
                    'username': user.username
                })
                
                resp = make_response(redirect(url_for('dashboard')))
                set_access_cookies(resp, access_token)
                flash(f'Welcome back, {user.username}!', 'success')
                return resp

            except Exception as e:
                flash('Login failed. Please try again.', 'danger')
                return redirect(url_for('login'))
        
        return render_template('login.html')