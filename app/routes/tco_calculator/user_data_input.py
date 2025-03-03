from flask import Blueprint, render_template, request
from app.models import Vehicle
from app.database import db
from app.services.data.vehicle_api import EPAFuelEconomyService

user_data_input_bp = Blueprint('user_data_input', __name__, url_prefix='/user-data-input')


@user_data_input_bp.route('/')
def landing():
    # Get years from EPA API instead of database
    years = EPAFuelEconomyService.get_years()
    return render_template('pages/tco_calculator.html', years=years)


@user_data_input_bp.route('/makes')
def get_makes():
    """Get makes for a specific year"""
    year_param = next((k for k in request.args.keys() if k.startswith('year')), None)
    year = request.args.get(year_param)
    
    if year and year.isdigit():
        makes = EPAFuelEconomyService.get_makes(int(year))
    else:
        makes = []
    
    return render_template('partials/makes.html', makes=makes)


@user_data_input_bp.route('/models')
def get_models():
    """Get models for a specific make and year"""
    year_param = next((k for k in request.args.keys() if k.startswith('year')), None)
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    
    vehicle_num = year_param[-1] if year_param else None
    year = request.args.get(f'year{vehicle_num}')
    make = request.args.get(f'make{vehicle_num}')
    
    if year and year.isdigit() and make:
        models = EPAFuelEconomyService.get_models(make, int(year))
    else:
        models = []
    
    return render_template('partials/models.html', models=models)


@user_data_input_bp.route('/fuel-types')
def get_fuel_types():
    """Get fuel types for a specific make/model/year"""
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    vehicle_num = make_param[-1] if make_param else None
    
    make = request.args.get(f'make{vehicle_num}')
    model = request.args.get(f'model{vehicle_num}')
    year = request.args.get(f'year{vehicle_num}')
    
    # Validate inputs
    if not all([make, model, year]):
        fuel_types = EPAFuelEconomyService.default_fuel_types()
    else:
        try:
            year = int(year)
            fuel_types = EPAFuelEconomyService.get_fuel_types(make, model, year)
        except (ValueError, TypeError) as e:
            print(f"Error converting year to integer: {e}")
            fuel_types = EPAFuelEconomyService.default_fuel_types()
    
    return render_template('partials/fuel_types.html', fuel_types=fuel_types)




