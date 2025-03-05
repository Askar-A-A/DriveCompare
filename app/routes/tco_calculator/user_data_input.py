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
    
    vehicle_num = year_param[-1] if year_param else None
    return render_template('partials/vehicle_selection/makes.html', makes=makes, vehicle_num=vehicle_num)


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
    
    return render_template('partials/vehicle_selection/models.html', models=models, vehicle_num=vehicle_num)


@user_data_input_bp.route('/fuel-types')
def get_fuel_types():
    """Get fuel types for a specific make/model/year"""
    # Find which vehicle we're dealing with by checking parameter names
    make_param = next((k for k in request.args.keys() if k.startswith('make')), None)
    vehicle_num = make_param[-1] if make_param else None
    
    make = request.args.get(f'make{vehicle_num}')
    model = request.args.get(f'model{vehicle_num}')
    year = request.args.get(f'year{vehicle_num}')
    
    # Print debug information
    print(f"Getting fuel types for vehicle {vehicle_num}: {make} {model} {year}")
    
    # Validate inputs
    if not all([make, model, year]):
        print("Missing required parameters, using default fuel types")
        fuel_types = EPAFuelEconomyService.default_fuel_types()
    else:
        try:
            year = int(year)
            fuel_types = EPAFuelEconomyService.get_fuel_types(make, model, year)
            # Print the fuel types for debugging
            print(f"Fuel types returned: {fuel_types}")
        except (ValueError, TypeError) as e:
            print(f"Error converting year to integer: {e}")
            fuel_types = EPAFuelEconomyService.default_fuel_types()
    
    # Pass vehicle_num to the template
    return render_template('partials/vehicle_selection/fuel_types.html', fuel_types=fuel_types, vehicle_num=vehicle_num)


@user_data_input_bp.route('/toggle-comparison')
def toggle_comparison():
    """Toggle between single and comparison view"""
    show_comparison = request.args.get('show') == 'true'
    
    # If showing comparison, we need to pass the years for the dropdown
    years = None
    if show_comparison:
        years = EPAFuelEconomyService.get_years()
        
    return render_template('partials/vehicle_selection/comparison_toggle.html', 
                          show_comparison=show_comparison,
                          years=years)




