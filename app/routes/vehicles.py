from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Vehicle, TCOComparison
from app.database import db
from sqlalchemy import func, desc
from flask_login import current_user

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@vehicles_bp.route('/')
def index():
    """Display the user's vehicle library"""
    page = request.args.get('page', 1, type=int)
    per_page = 9  # 9 vehicles per page (3x3 grid)
    
    # Get all vehicles that have been analyzed
    query = db.session.query(
        Vehicle,
        func.count(TCOComparison.id).label('analysis_count'),
        func.max(TCOComparison.created_at).label('last_analyzed')
    ).join(
        TCOComparison, 
        ((TCOComparison.vehicle1_id == Vehicle.id) | (TCOComparison.vehicle2_id == Vehicle.id))
    )
    
    # If user is logged in, only show their vehicles
    if current_user.is_authenticated:
        query = query.filter(TCOComparison.user_id == current_user.id)
    
    # Group by vehicle and order by most recently analyzed
    query = query.group_by(Vehicle.id).order_by(desc('last_analyzed'))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Process the results to add the analysis_count and last_analyzed to each vehicle
    vehicles = []
    for vehicle, analysis_count, last_analyzed in pagination.items:
        vehicle.analysis_count = analysis_count
        vehicle.last_analyzed = last_analyzed
        vehicles.append(vehicle)
    
    # Get unique years for the filter dropdown
    years = db.session.query(Vehicle.year).distinct().order_by(Vehicle.year.desc()).all()
    years = [year[0] for year in years]
    
    return render_template(
        'pages/vehicles.html',
        vehicles=vehicles,
        pagination=pagination,
        years=years
    )

@vehicles_bp.route('/search', methods=['POST'])
def search():
    """Search vehicles and return partial HTML"""
    search_term = request.form.get('search', '')
    
    # Query vehicles matching the search term
    query = db.session.query(
        Vehicle,
        func.count(TCOComparison.id).label('analysis_count'),
        func.max(TCOComparison.created_at).label('last_analyzed')
    ).join(
        TCOComparison, 
        ((TCOComparison.vehicle1_id == Vehicle.id) | (TCOComparison.vehicle2_id == Vehicle.id))
    )
    
    # Apply search filter
    if search_term:
        search_filter = (
            Vehicle.make.ilike(f'%{search_term}%') |
            Vehicle.model.ilike(f'%{search_term}%') |
            Vehicle.fuel_type.ilike(f'%{search_term}%')
        )
        query = query.filter(search_filter)
    
    # If user is logged in, only show their vehicles
    if current_user.is_authenticated:
        query = query.filter(TCOComparison.user_id == current_user.id)
    
    # Group and order
    query = query.group_by(Vehicle.id).order_by(desc('last_analyzed'))
    
    # Get results
    results = query.all()
    
    # Process the results
    vehicles = []
    for vehicle, analysis_count, last_analyzed in results:
        vehicle.analysis_count = analysis_count
        vehicle.last_analyzed = last_analyzed
        vehicles.append(vehicle)
    
    # Render just the vehicles grid
    return render_template('partials/vehicles/vehicles_grid.html', vehicles=vehicles)

@vehicles_bp.route('/filter', methods=['POST'])
def filter():
    """Filter vehicles and return partial HTML"""
    vehicle_type = request.form.get('vehicle_type', '')
    year = request.form.get('year', '')
    
    # Base query
    query = db.session.query(
        Vehicle,
        func.count(TCOComparison.id).label('analysis_count'),
        func.max(TCOComparison.created_at).label('last_analyzed')
    ).join(
        TCOComparison, 
        ((TCOComparison.vehicle1_id == Vehicle.id) | (TCOComparison.vehicle2_id == Vehicle.id))
    )
    
    # Apply filters
    if vehicle_type:
        if vehicle_type == 'ev':
            query = query.filter(Vehicle.fuel_type.ilike('%electric%'))
        elif vehicle_type == 'hybrid':
            query = query.filter(Vehicle.fuel_type.ilike('%hybrid%'))
        elif vehicle_type == 'ice':
            query = query.filter(~Vehicle.fuel_type.ilike('%electric%'), ~Vehicle.fuel_type.ilike('%hybrid%'))
    
    if year and year.isdigit():
        query = query.filter(Vehicle.year == int(year))
    
    # If user is logged in, only show their vehicles
    if current_user.is_authenticated:
        query = query.filter(TCOComparison.user_id == current_user.id)
    
    # Group and order
    query = query.group_by(Vehicle.id).order_by(desc('last_analyzed'))
    
    # Get results
    results = query.all()
    
    # Process the results
    vehicles = []
    for vehicle, analysis_count, last_analyzed in results:
        vehicle.analysis_count = analysis_count
        vehicle.last_analyzed = last_analyzed
        vehicles.append(vehicle)
    
    # Render just the vehicles grid
    return render_template('partials/vehicles/vehicles_grid.html', vehicles=vehicles)

@vehicles_bp.route('/<int:vehicle_id>/history')
def view_history(vehicle_id):
    """View TCO analysis history for a specific vehicle"""
    # Get the vehicle
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Get all TCO comparisons involving this vehicle
    query = TCOComparison.query.filter(
        (TCOComparison.vehicle1_id == vehicle_id) | 
        (TCOComparison.vehicle2_id == vehicle_id)
    )
    
    # If user is logged in, only show their comparisons
    if current_user.is_authenticated:
        query = query.filter(TCOComparison.user_id == current_user.id)
    
    # Order by most recent first
    comparisons = query.order_by(TCOComparison.created_at.desc()).all()
    
    return render_template(
        'pages/vehicle_history.html',
        vehicle=vehicle,
        comparisons=comparisons
    )

@vehicles_bp.route('/<int:vehicle_id>/analysis/<int:comparison_id>')
def view_analysis(vehicle_id, comparison_id):
    """View a specific TCO analysis"""
    # Get the vehicle and comparison
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    comparison = TCOComparison.query.get_or_404(comparison_id)
    
    # Verify this comparison involves this vehicle
    if comparison.vehicle1_id != vehicle_id and comparison.vehicle2_id != vehicle_id:
        return redirect(url_for('vehicles.view_history', vehicle_id=vehicle_id))
    
    # Get the comparison data from the JSON field
    data = comparison.get_comparison_data()
    
    # Debug: Print the data to the console
    print(f"Comparison data: {data}")
    
    return render_template(
        'pages/vehicle_analysis.html',
        vehicle=vehicle,
        comparison=comparison,
        data=data
    )