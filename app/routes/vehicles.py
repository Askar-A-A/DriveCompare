from flask import Blueprint, render_template

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicles_bp.route('/')
def landing():
    return render_template('pages/vehicles.html', name='Vehicles')