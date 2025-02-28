from flask import Blueprint, render_template, request
from app.models import Vehicle
from app.database import db

user_data_input_bp = Blueprint('user_data_input', __name__, url_prefix='/user-data-input')


@user_data_input_bp.route('/')
def landing():
    makes = db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()
    return render_template('pages/tco_calculator.html', makes=makes)


@user_data_input_bp.route('/vehicle-types')
def get_vehicle_types():
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    make = request.args.get(make_param)
    types = db.session.query(Vehicle.type).filter(
        Vehicle.make == make
    ).distinct().order_by(Vehicle.type).all()
    
    return render_template('partials/vehicle_types.html', types=types)


@user_data_input_bp.route('/years')
def get_years():
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    vehicle_num = make_param[-1] if make_param else None  
    make = request.args.get(f'make{vehicle_num}')
    vehicle_type = request.args.get(f'type{vehicle_num}')
    years = db.session.query(Vehicle.year).filter(
        Vehicle.make == make,
        Vehicle.type == vehicle_type
    ).distinct().order_by(Vehicle.year.desc()).all()
    return render_template('partials/years.html', years=years)


@user_data_input_bp.route('/models')
def get_models():
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    vehicle_num = make_param[-1] if make_param else None
    make = request.args.get(f'make{vehicle_num}')
    vehicle_type = request.args.get(f'type{vehicle_num}')
    year = request.args.get(f'year{vehicle_num}')
    
    models = db.session.query(Vehicle.model).filter(
        Vehicle.make == make,
        Vehicle.type == vehicle_type,
        Vehicle.year == year
    ).distinct().order_by(Vehicle.model).all()
    return render_template('partials/models.html', models=models)


