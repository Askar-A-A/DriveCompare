from flask import Blueprint, request, render_template
from app.models import Vehicle, TCOComparison
from app.services.business_logic.depreciation_service import DepreciationService
from app.services.visualization.depreciation_visual import ChartService
from app.database import db
from flask_login import current_user
import re

depreciation_bp = Blueprint('depreciation', __name__, url_prefix='/depreciation')

@depreciation_bp.route('/compare-multiple-vehicles', methods=['POST'])
def compare_multiple_vehicles():
    """Compare multiple vehicles based on form data and return HTML results"""
    try:
        # Get user inputs for mileage and ownership period
        annual_mileage = int(request.form.get('annualMiles', 12000))
        years = int(request.form.get('ownershipYears', 5))
        
        # Get the indices of all vehicles
        vehicle_indices = request.form.getlist('vehicle_indices')
        
        if not vehicle_indices:
            return "<div class='alert alert-danger'>Please add at least one vehicle to compare</div>"
        
        # Process each vehicle
        vehicles = []
        vehicle_data = []
        vehicle_objects = []
        
        for index in vehicle_indices:
            make = request.form.get(f'make_{index}')
            vehicle_type = request.form.get(f'type_{index}')
            year = request.form.get(f'year_{index}')
            model = request.form.get(f'model_{index}')
            fuel_type = request.form.get(f'fuelType_{index}')
            
            if not all([make, year, model, fuel_type]):
                continue
            
            # Create vehicle dictionary
            vehicle_dict = {
                'make': make,
                'type': vehicle_type,
                'year': int(year),
                'model': model,
                'fuel_type': fuel_type
            }
            
            # Get the vehicle object
            vehicle_obj = DepreciationService.get_or_create_vehicle(
                make, model, int(year), fuel_type, vehicle_type
            )
            
            vehicles.append(vehicle_dict)
            vehicle_objects.append(vehicle_obj)
        
        if len(vehicles) < 1:
            return "<div class='alert alert-danger'>No valid vehicles found</div>"
        
        # Calculate depreciation for each vehicle
        for vehicle in vehicles:
            depreciation = DepreciationService.calculate_depreciation(
                vehicle,
                years=years,
                annual_mileage=annual_mileage
            )
            vehicle_data.append(depreciation)
        
        # Generate comparison data structure
        comparison_data = {
            'vehicles': vehicle_data,
            'count': len(vehicles)
        }
        
        # Generate multi-vehicle chart
        depreciation_chart_url = ChartService.generate_multi_vehicle_chart(
            vehicle_objects, vehicle_data
        )
        
        retention_chart_url = ChartService.generate_multi_vehicle_retention_chart(
            vehicle_objects, vehicle_data
        )
        
        # Create a TCOComparison record for the primary vehicle
        primary_vehicle = vehicle_objects[0]
        comparison_record = TCOComparison(
            # Vehicle 1 details
            vehicle1_id=primary_vehicle.id,
            vehicle1_make=primary_vehicle.make,
            vehicle1_model=primary_vehicle.model,
            vehicle1_year=primary_vehicle.year,
            vehicle1_fuel_type=primary_vehicle.fuel_type,
            vehicle1_type=primary_vehicle.type,
            
            # Analysis parameters
            annual_mileage=annual_mileage,
            ownership_years=years,
            
            # Is this a comparison?
            is_comparison=len(vehicles) > 1
        )
        
        # If there's a second vehicle, add it to the comparison record
        if len(vehicles) > 1:
            second_vehicle = vehicle_objects[1]
            comparison_record.vehicle2_id = second_vehicle.id
            comparison_record.vehicle2_make = second_vehicle.make
            comparison_record.vehicle2_model = second_vehicle.model
            comparison_record.vehicle2_year = second_vehicle.year
            comparison_record.vehicle2_fuel_type = second_vehicle.fuel_type
            comparison_record.vehicle2_type = second_vehicle.type
        
        # Store the comparison data
        comparison_data_to_store = {}
        
        # Add data for each vehicle
        for i, (vehicle_obj, vehicle_depr) in enumerate(zip(vehicle_objects, vehicle_data)):
            vehicle_key = f'vehicle{i+1}'
            comparison_data_to_store[vehicle_key] = {
                'initial_cost': vehicle_depr.get('initial_price', 0),
                'depreciation_cost': vehicle_depr.get('total_depreciation', 0),
                'fuel_cost': 0,  # These would need to be calculated
                'maintenance_cost': 0,
                'insurance_cost': 0,
                'total_cost': vehicle_depr.get('total_depreciation', 0),  # Simplified for now
                'resale_value': vehicle_depr.get('final_value', 0)
            }
        
        comparison_record.set_comparison_data(comparison_data_to_store)
        
        # Store the charts
        comparison_record.depreciation_chart = depreciation_chart_url
        comparison_record.retention_chart = retention_chart_url
        
        # If user is logged in, associate with user
        if current_user.is_authenticated:
            comparison_record.user_id = current_user.id
        
        # Save to database
        db.session.add(comparison_record)
        db.session.commit()
        
        # Render results template
        return render_template(
            'partials/multi_vehicle_results.html',
            vehicles=vehicle_objects,
            vehicle_data=vehicle_data,
            depreciation_chart_url=depreciation_chart_url,
            retention_chart_url=retention_chart_url,
            years=years,
            annual_mileage=annual_mileage,
            vehicle_count=len(vehicles)
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<div class='alert alert-danger'>Error: {str(e)}</div>"
