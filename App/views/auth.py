from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from .index import index_views
from App.controllers.auth import login
from App.controllers.tenant import get_all_tenants  
from App.controllers.landlord import get_all_landlords

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    
@auth_views.route('/landlords', methods=['GET'])
def get_landlord_page():
    landlords = get_all_landlords()
    return render_template('users.html', users=landlords, role="Landlords")

@auth_views.route('/tenants', methods=['GET'])
def get_tenant_page():
    tenants = get_all_tenants()
    return render_template('users.html', users=tenants, role="Tenants")

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer or url_for('index_views.index_page'))
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer or url_for('index_views.index_page'))
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''
@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    token = login(data['username'], data['password'])
    if not token:
        return jsonify(message='Bad username or password given'), 401
    response = jsonify(access_token=token) 
    set_access_cookies(response, token)
    return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({
        'message': f"Logged in as: {current_user.username}",
        'id': current_user.id,
        'type': current_user.__class__.__name__  # e.g., Tenant or Landlord
    })

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response
