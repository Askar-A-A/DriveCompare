from flask import Blueprint, render_template, request
from app.models import Vehicle, TCOComparison
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


@user_data_input_bp.route('/prefill/<int:vehicle_id>')
def prefill(vehicle_id):
    """Pre-fill the TCO calculator with a specific vehicle"""
    # Get the vehicle from the database
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Get years for the dropdown
    years = EPAFuelEconomyService.get_years()
    
    # Pre-select the vehicle's year in the dropdown
    selected_year = vehicle.year
    
    # Get makes for the selected year
    makes = EPAFuelEconomyService.get_makes(selected_year)
    
    # Pre-select the vehicle's make
    selected_make = vehicle.make
    
    # Get models for the selected year and make
    models = EPAFuelEconomyService.get_models(selected_year, selected_make)
    
    # Pre-select the vehicle's model
    selected_model = vehicle.model
    
    # Get fuel types for the selected year, make, and model
    fuel_types = EPAFuelEconomyService.get_fuel_types(selected_year, selected_make, selected_model)
    
    # Pre-select the vehicle's fuel type
    selected_fuel_type = vehicle.fuel_type
    
    return render_template(
        'pages/tco_calculator.html',
        years=years,
        makes=makes,
        models=models,
        fuel_types=fuel_types,
        selected_year=selected_year,
        selected_make=selected_make,
        selected_model=selected_model,
        selected_fuel_type=selected_fuel_type,
        prefilled_vehicle=vehicle
    )


@user_data_input_bp.route('/recreate/<int:comparison_id>')
def recreate(comparison_id):
    """Recreate a previous TCO comparison"""
    # Get the comparison from the database
    comparison = TCOComparison.query.get_or_404(comparison_id)
    
    # Get years for the dropdown
    years = EPAFuelEconomyService.get_years()
    
    # Set up vehicle 1
    selected_year1 = comparison.vehicle1_year
    selected_make1 = comparison.vehicle1_make
    selected_model1 = comparison.vehicle1_model
    selected_fuel_type1 = comparison.vehicle1_fuel_type
    
    # Get dropdown options for vehicle 1
    makes1 = EPAFuelEconomyService.get_makes(selected_year1)
    models1 = EPAFuelEconomyService.get_models(selected_year1, selected_make1)
    fuel_types1 = EPAFuelEconomyService.get_fuel_types(selected_year1, selected_make1, selected_model1)
    
    # Set up vehicle 2 if this was a comparison
    show_comparison = comparison.is_comparison
    selected_year2 = None
    selected_make2 = None
    selected_model2 = None
    selected_fuel_type2 = None
    makes2 = None
    models2 = None
    fuel_types2 = None
    
    if show_comparison:
        selected_year2 = comparison.vehicle2_year
        selected_make2 = comparison.vehicle2_make
        selected_model2 = comparison.vehicle2_model
        selected_fuel_type2 = comparison.vehicle2_fuel_type
        
        # Get dropdown options for vehicle 2
        makes2 = EPAFuelEconomyService.get_makes(selected_year2)
        models2 = EPAFuelEconomyService.get_models(selected_year2, selected_make2)
        fuel_types2 = EPAFuelEconomyService.get_fuel_types(selected_year2, selected_make2, selected_model2)
    
    # Set the analysis parameters
    annual_mileage = comparison.annual_mileage
    ownership_years = comparison.ownership_years
    
    return render_template(
        'pages/tco_calculator.html',
        years=years,
        makes1=makes1,
        models1=models1,
        fuel_types1=fuel_types1,
        selected_year1=selected_year1,
        selected_make1=selected_make1,
        selected_model1=selected_model1,
        selected_fuel_type1=selected_fuel_type1,
        
        show_comparison=show_comparison,
        makes2=makes2,
        models2=models2,
        fuel_types2=fuel_types2,
        selected_year2=selected_year2,
        selected_make2=selected_make2,
        selected_model2=selected_model2,
        selected_fuel_type2=selected_fuel_type2,
        
        annual_mileage=annual_mileage,
        ownership_years=ownership_years,
        recreated_comparison=comparison
    )




