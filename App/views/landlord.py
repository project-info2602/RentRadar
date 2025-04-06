from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from App.controllers import create_landlord, get_all_landlords, get_all_landlords_json

landlord_views = Blueprint('landlord_views', __name__, template_folder='../templates')

@landlord_views.route('/landlords', methods=['GET'])
def get_landlords_page():
    landlords = get_all_landlords()
    return render_template('landlords.html', landlords=landlords)

@landlord_views.route('/landlords', methods=['POST'])
def create_landlord_action():
    data = request.form
    flash(f"Landlord {data['username']} created!")
    create_landlord(data['username'], data['password'])
    return redirect(url_for('landlord_views.get_landlords_page'))

@landlord_views.route('/api/landlords', methods=['GET'])
def get_landlords_api():
    return jsonify(get_all_landlords_json())

@landlord_views.route('/api/landlords', methods=['POST'])
def create_landlord_api():
    data = request.json
    landlord = create_landlord(data['username'], data['password'])
    return jsonify({'message': f"Landlord {landlord.username} created with id {landlord.id}"})
