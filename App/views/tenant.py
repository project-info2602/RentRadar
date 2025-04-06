from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from App.controllers import create_tenant, get_all_tenants, get_all_tenants_json

tenant_views = Blueprint('tenant_views', __name__, template_folder='../templates')

# Web view - list tenants
@tenant_views.route('/tenants', methods=['GET'])
def get_tenant_page():
    tenants = get_all_tenants()
    return render_template('tenants.html', tenants=tenants)

# Web form - create tenant
@tenant_views.route('/tenants', methods=['POST'])
def create_tenant_action():
    data = request.form
    tenant = create_tenant(data['username'], data['password'])
    flash(f"Tenant {tenant.username} created!")
    return redirect(url_for('tenant_views.get_tenant_page'))

# API endpoint - list tenants
@tenant_views.route('/api/tenants', methods=['GET'])
def get_tenants_json():
    tenants = get_all_tenants_json()
    return jsonify(tenants)

# API endpoint - create tenant
@tenant_views.route('/api/tenants', methods=['POST'])
def create_tenant_endpoint():
    data = request.json
    tenant = create_tenant(data['username'], data['password'])
    return jsonify({'message': f"Tenant {tenant.username} created with id {tenant.id}"})
