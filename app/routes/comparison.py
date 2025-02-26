from flask import Blueprint, render_template, request
from app.models import Vehicle
from app.database import db

comparison_bp = Blueprint('comparison', __name__, url_prefix='/comparison')

# Main page route
@comparison_bp.route('/')
def landing():
    # Get initial makes for the dropdowns
    makes = db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()
    return render_template('pages/comparison.html', makes=makes)

@comparison_bp.route('/vehicle-types')
def get_vehicle_types():
    # Get the make parameter (could be make1 or make2)
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    make = request.args.get(make_param)
    
    print(f"Received make param: {make_param}, value: {make}")  # Debug print
    
    types = db.session.query(Vehicle.type).filter(
        Vehicle.make == make
    ).distinct().order_by(Vehicle.type).all()
    
    print(f"Found types: {types}")  # Debug print
    return render_template('partials/vehicle_types.html', types=types)

@comparison_bp.route('/years')
def get_years():
    # Get vehicle number from the parameter names
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    vehicle_num = make_param[-1] if make_param else None  # Gets '1' or '2' from 'make1' or 'make2'
    
    make = request.args.get(f'make{vehicle_num}')
    vehicle_type = request.args.get(f'type{vehicle_num}')
    
    years = db.session.query(Vehicle.year).filter(
        Vehicle.make == make,
        Vehicle.type == vehicle_type
    ).distinct().order_by(Vehicle.year.desc()).all()
    return render_template('partials/years.html', years=years)

@comparison_bp.route('/models')
def get_models():
    # Get vehicle number from the parameter names
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


