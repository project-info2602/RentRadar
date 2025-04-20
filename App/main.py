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
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                role = request.form.get('role')
                lease_code = request.form.get('lease_code', '')

                if not all([username, email, password, confirm_password, role]):
                    flash('All fields are required', 'danger')
                    return redirect(url_for('register'))

                if password != confirm_password:
                    flash('Passwords do not match', 'danger')
                    return redirect(url_for('register'))

                if role == 'landlord':
                    if Landlord.query.filter((Landlord.username == username) | (Landlord.email == email)).first():
                        flash('Username or email already exists', 'danger')
                        return redirect(url_for('register'))

                    landlord = Landlord(username=username, email=email, password=password)
                    db.session.add(landlord)
                    db.session.commit()
                    flash('Landlord account created successfully! Please login.', 'success')
                    return redirect(url_for('login'))

                elif role == 'tenant':
                    apartment = Apartment.query.filter_by(lease_code=lease_code).first()
                    if not apartment:
                        flash('Invalid lease code', 'danger')
                        return redirect(url_for('register'))

                    if Tenant.query.filter((Tenant.username == username) | (Tenant.email == email)).first():
                        flash('Username or email already exists', 'danger')
                        return redirect(url_for('register'))

                    tenant = Tenant(
                        username=username,
                        email=email,
                        password=password,
                        lease_code=lease_code
                    )
                    db.session.add(tenant)
                    db.session.commit()
                    flash('Tenant account created successfully! Please login.', 'success')
                    return redirect(url_for('login'))

                else:
                    flash('Invalid role selected', 'danger')
                    
            except Exception as e:
                flash(f'Registration error: {str(e)}', 'danger')
                return redirect(url_for('register'))
        
        return render_template('register.html')

    @app.route('/register/check_lease', methods=['POST'])
    def check_lease_code():
        lease_code = request.json.get('lease_code')
        apartment = Apartment.query.filter_by(lease_code=lease_code).first()
        
        if apartment:
            return jsonify({
                'valid': True,
                'apartment': {
                    'title': apartment.title,
                    'location': apartment.location,
                    'price': apartment.price
                }
            })
        return jsonify({'valid': False})

    @app.route('/logout')
    def logout():
        response = make_response(redirect(url_for('index')))
        unset_jwt_cookies(response)
        flash('You have been logged out', 'success')
        return response

    # Dashboard
    @app.route('/dashboard')
    @jwt_required()
    def dashboard():
        current_user = get_jwt_identity()
        user_id = current_user.get('id')
        role = current_user.get('role')

        if role == 'landlord':
            user = Landlord.query.get(user_id)
            apartments = user.apartments_owned
            return render_template('landlord_dashboard.html', apartments=apartments, user=user)
        else:
            user = Tenant.query.get(user_id)
            apartment = Apartment.query.get(user.apartment_id)
            has_reviewed = Review.query.filter_by(tenant_id=user.id, apartment_id=user.apartment_id).first() is not None
            return render_template('tenant_dashboard.html', apartment=apartment, user=user, has_reviewed=has_reviewed)
        
    # Apartment Routes
    @app.route('/apartments')
    def apartments_list():
        apartments = Apartment.query.all()
        return render_template('apartments.html', apartments=apartments, locations=LOCATIONS, amenities=AMENITIES)

    @app.route('/apartments/<int:apartment_id>')
    @jwt_required(optional=True)
    def apartment_detail(apartment_id):
        apartment = Apartment.query.get_or_404(apartment_id)
        reviews = Review.query.filter_by(apartment_id=apartment_id).all()
        tenants = Tenant.query.filter_by(apartment_id=apartment_id).all()
        
        current_user = get_jwt_identity()
        has_reviewed = False
        can_review = False
        
        if current_user and current_user.get('role') == 'tenant':
            tenant = Tenant.query.get(current_user.get('id'))
            if tenant and tenant.apartment_id == apartment_id:
                can_review = True
                has_reviewed = Review.query.filter_by(tenant_id=tenant.id, apartment_id=apartment_id).first() is not None
        
        return render_template('apartment_detail.html', 
                            apartment=apartment, 
                            reviews=reviews, 
                            tenants=tenants,
                            has_reviewed=has_reviewed,
                            can_review=can_review,
                            current_user=current_user)
    
    @app.route('/apartments/create', methods=['GET', 'POST'])
    @jwt_required()
    def create_apartment():
        current_user = get_jwt_identity()
        if current_user.get('role') != 'landlord':
            flash('Only landlords can create apartments', 'danger')
            return redirect(url_for('dashboard'))

        landlord = Landlord.query.get(current_user.get('id'))
        
        if request.method == 'POST':
            try:
                title = request.form.get('title')
                description = request.form.get('description')
                location = request.form.get('location')
                price = float(request.form.get('price'))
                amenities = request.form.getlist('amenities')
                
                if not all([title, description, location, price, amenities]):
                    flash('All fields are required', 'danger')
                    return redirect(url_for('create_apartment'))
                
                apartment = Apartment(
                    title=title,
                    description=description,
                    location=location,
                    price=price,
                    landlord_id=landlord.id,
                    amenities=amenities
                )
                
                db.session.add(apartment)
                db.session.commit()
                flash(f'Apartment created successfully! Lease code: {apartment.lease_code}', 'success')
                return redirect(url_for('apartment_detail', apartment_id=apartment.id))
            
            except ValueError as e:
                db.session.rollback()
                flash(f'Validation error: {str(e)}', 'danger')
                return redirect(url_for('create_apartment'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating apartment: {str(e)}', 'danger')
                return redirect(url_for('create_apartment'))
        
        return render_template('create_apartment.html', locations=LOCATIONS, amenities=AMENITIES)

    @app.route('/apartments/<int:apartment_id>/edit', methods=['GET', 'POST'])
    @jwt_required()
    def edit_apartment(apartment_id):
        current_user = get_jwt_identity()
        apartment = Apartment.query.get_or_404(apartment_id)
        
        if current_user.get('role') != 'landlord' or current_user.get('id') != apartment.landlord_id:
            flash('You can only edit your own apartments', 'danger')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            try:
                apartment.title = request.form.get('title')
                apartment.description = request.form.get('description')
                apartment.location = request.form.get('location')
                apartment.price = float(request.form.get('price'))
                apartment.amenities = request.form.getlist('amenities')
                
                apartment.validate()
                db.session.commit()
                flash('Apartment updated successfully!', 'success')
                return redirect(url_for('apartment_detail', apartment_id=apartment_id))
            
            except ValueError as e:
                db.session.rollback()
                flash(f'Validation error: {str(e)}', 'danger')
                return redirect(url_for('edit_apartment', apartment_id=apartment_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating apartment: {str(e)}', 'danger')
                return redirect(url_for('edit_apartment', apartment_id=apartment_id))
        
        return render_template('edit_apartment.html', 
                            apartment=apartment,
                            locations=LOCATIONS,
                            amenities=AMENITIES)       

    @app.route('/apartments/<int:apartment_id>/delete', methods=['POST'])
    @jwt_required()
    def delete_apartment(apartment_id):
        current_user = get_jwt_identity()
        apartment = Apartment.query.get_or_404(apartment_id)
        
        if current_user.get('role') != 'landlord' or current_user.get('id') != apartment.landlord_id:
            flash('You cannot delete this apartment', 'danger')
            return redirect(url_for('dashboard'))
        
        try:
            db.session.delete(apartment)
            db.session.commit()
            flash('Apartment deleted successfully', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting apartment: {str(e)}', 'danger')
            return redirect(url_for('apartment_detail', apartment_id=apartment_id))

    # Review Routes
    @app.route('/apartments/<int:apartment_id>/reviews/add', methods=['GET', 'POST'])
    @jwt_required()
    def add_review(apartment_id):
        current_user = get_jwt_identity()
        if current_user.get('role') != 'tenant':
            flash('Only tenants can add reviews', 'danger')
            return redirect(url_for('apartment_detail', apartment_id=apartment_id))
        
        tenant = Tenant.query.get(current_user.get('id'))
        apartment = Apartment.query.get_or_404(apartment_id)
        
        if not tenant or tenant.apartment_id != apartment_id:
            flash('You can only review your assigned apartment', 'danger')
            return redirect(url_for('apartment_detail', apartment_id=apartment_id))
        
        # Check if already reviewed
        existing_review = Review.query.filter_by(
            tenant_id=tenant.id,
            apartment_id=apartment_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this apartment', 'warning')
            return redirect(url_for('apartment_detail', apartment_id=apartment_id))
        
        if request.method == 'POST':
            try:
                review = Review(
                    tenant_id=tenant.id,
                    apartment_id=apartment_id,
                    rating=int(request.form.get('rating')),
                    comment=request.form.get('comment')
                )
                db.session.add(review)
                db.session.commit()
                flash('Review added successfully!', 'success')
                return redirect(url_for('apartment_detail', apartment_id=apartment_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding review: {str(e)}', 'danger')
                return redirect(url_for('add_review', apartment_id=apartment_id))
        
        return render_template('add_review.html', apartment=apartment) 
    
    @app.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
    @jwt_required()
    def edit_review(review_id):
        current_user = get_jwt_identity()
        review = Review.query.get_or_404(review_id)
        
        if current_user.get('role') != 'tenant' or current_user.get('id') != review.tenant_id:
            flash('You can only edit your own reviews', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                # Validate rating is between 1-5
                rating = int(request.form.get('rating'))
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5")
                
                review.rating = rating
                review.comment = request.form.get('comment')
                db.session.commit()
                
                flash('Review updated successfully!', 'success')
                return redirect(url_for('apartment_detail', apartment_id=review.apartment_id))
            except ValueError as e:
                db.session.rollback()
                flash(str(e), 'danger')
                return redirect(url_for('edit_review', review_id=review_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating review: {str(e)}', 'danger')
                return redirect(url_for('edit_review', review_id=review_id))
        
        return render_template('edit_review.html', review=review)

    @app.route('/reviews/<int:review_id>/delete', methods=['POST'])
    @jwt_required()
    def delete_review(review_id):
        current_user = get_jwt_identity()
        review = Review.query.get_or_404(review_id)
        
        if current_user.get('role') != 'tenant' or current_user.get('id') != review.tenant_id:
            flash('You can only delete your own reviews', 'danger')
            return redirect(url_for('dashboard'))
        
        try:
            apartment_id = review.apartment_id
            db.session.delete(review)
            db.session.commit()
            flash('Review deleted successfully!', 'success')
            return redirect(url_for('apartment_detail', apartment_id=apartment_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting review: {str(e)}', 'danger')
            return redirect(url_for('apartment_detail', apartment_id=review.apartment_id))
        
    # Search
    @app.route('/search', methods=['GET'])
    def search():
        location = request.args.get('location')
        amenities = request.args.getlist('amenities')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        query = Apartment.query
        
        if location and location in LOCATIONS:
            query = query.filter_by(location=location)
        
        apartments = query.all()
        
        if amenities:
            apartments = [apt for apt in apartments 
                         if all(amenity in apt.amenities for amenity in amenities)]
        
        if min_price is not None:
            apartments = [apt for apt in apartments if apt.price >= min_price]
        
        if max_price is not None:
            apartments = [apt for apt in apartments if apt.price <= max_price]
        
        return render_template('search_results.html', 
                            apartments=apartments, 
                            search_params=request.args,
                            locations=LOCATIONS,
                            amenities=AMENITIES)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
       