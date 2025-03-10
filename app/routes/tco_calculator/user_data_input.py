from flask import Blueprint, render_template, request, session, jsonify
from app.models import Vehicle, TCOComparison
from app.database import db
from app.services.data.vehicle_api import EPAFuelEconomyService

user_data_input_bp = Blueprint('user_data_input', __name__, url_prefix='/user-data-input')


@user_data_input_bp.route('/')
def landing():
    years = EPAFuelEconomyService.get_years()
    if 'vehicle_counter' not in session:
        session['vehicle_counter'] = 0
    return render_template('pages/tco_calculator.html', years=years)


@user_data_input_bp.route('/makes')
def get_makes():
    """Get makes for a specific year"""
    year = request.args.get('year')
    
    if year and year.isdigit():
        makes = EPAFuelEconomyService.get_makes(int(year))
    else:
        makes = []
    
    return render_template('partials/vehicle_selection/makes.html', makes=makes)


@user_data_input_bp.route('/models')
def get_models():
    """Get models for a specific make and year"""
    year = request.args.get('year')
    make = request.args.get('make')
    
    if year and year.isdigit() and make:
        models = EPAFuelEconomyService.get_models(make, int(year))
    else:
        models = []
    
    return render_template('partials/vehicle_selection/models.html', models=models)


@user_data_input_bp.route('/fuel-types')
def get_fuel_types():
    """Get fuel types for a specific make/model/year"""
    make = request.args.get('make')
    model = request.args.get('model')
    year = request.args.get('year')
    

    if not all([make, model, year]):
        fuel_types = EPAFuelEconomyService.default_fuel_types()
    else:
        try:
            year = int(year)
            fuel_types = EPAFuelEconomyService.get_fuel_types(make, model, year)
        except (ValueError, TypeError) as e:
            fuel_types = EPAFuelEconomyService.default_fuel_types()
    
    return render_template('partials/vehicle_selection/fuel_types.html', fuel_types=fuel_types)


@user_data_input_bp.route('/add-vehicle', methods=['POST'])
def add_vehicle():
    """Add a vehicle to the comparison list"""
    year = request.form.get('year')
    make = request.form.get('make')
    model = request.form.get('model')
    fuel_type = request.form.get('fuelType')
    vehicle_type = request.form.get('type', 'Auto')
    
    if not all([year, make, model, fuel_type]):
        return "<div class='alert alert-danger'>Please complete all vehicle fields</div>"
    
    if 'vehicle_counter' not in session:
        session['vehicle_counter'] = 0
    
    session['vehicle_counter'] += 1
    index = session['vehicle_counter']
    
    return render_template(
        'partials/vehicle_selection/selected_vehicle.html',
        index=index,
        year=year,
        make=make,
        model=model,
        fuel_type=fuel_type,
        vehicle_type=vehicle_type
    )


@user_data_input_bp.route('/remove-vehicle')
def remove_vehicle():
    """Remove a vehicle from the comparison list"""
    return ""


@user_data_input_bp.route('/prefill/<int:vehicle_id>')
def prefill(vehicle_id):
    """Pre-fill the TCO calculator with a specific vehicle"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    years = EPAFuelEconomyService.get_years()
    selected_year = vehicle.year

    makes = EPAFuelEconomyService.get_makes(selected_year)
    selected_make = vehicle.make

    models = EPAFuelEconomyService.get_models(selected_year, selected_make)
    selected_model = vehicle.model
    
    fuel_types = EPAFuelEconomyService.get_fuel_types(selected_year, selected_make, selected_model)
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


@user_data_input_bp.route('/toggle-comparison')
def toggle_comparison():
    """Toggle between single and comparison view"""
    show_comparison = request.args.get('show') == 'true'
    
    years = None
    if show_comparison:
        years = EPAFuelEconomyService.get_years()
        
    return render_template('partials/vehicle_selection/comparison_toggle.html', 
                          show_comparison=show_comparison,
                          years=years)


@user_data_input_bp.route('/recreate/<int:comparison_id>')
def recreate(comparison_id):
    """Recreate a previous TCO comparison"""
    comparison = TCOComparison.query.get_or_404(comparison_id)

    years = EPAFuelEconomyService.get_years()
    
    selected_year1 = comparison.vehicle1_year
    selected_make1 = comparison.vehicle1_make
    selected_model1 = comparison.vehicle1_model
    selected_fuel_type1 = comparison.vehicle1_fuel_type
    
    makes1 = EPAFuelEconomyService.get_makes(selected_year1)
    models1 = EPAFuelEconomyService.get_models(selected_year1, selected_make1)
    fuel_types1 = EPAFuelEconomyService.get_fuel_types(selected_year1, selected_make1, selected_model1)
    
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
        
        makes2 = EPAFuelEconomyService.get_makes(selected_year2)
        models2 = EPAFuelEconomyService.get_models(selected_year2, selected_make2)
        fuel_types2 = EPAFuelEconomyService.get_fuel_types(selected_year2, selected_make2, selected_model2)
    
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




