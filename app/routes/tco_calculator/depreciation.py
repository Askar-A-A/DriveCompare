from flask import Blueprint, request, render_template
from app.models import Vehicle, TCOComparison
from app.services.business_logic.depreciation_service import DepreciationService
from app.services.visualization.depreciation_visual import ChartService
from app.services.business_logic.comparison_storage_service import ComparisonStorageService
from app.database import db
from flask_login import current_user
import re

depreciation_bp = Blueprint('depreciation', __name__, url_prefix='/depreciation')

@depreciation_bp.route('/compare-multiple-vehicles', methods=['POST'])
def compare_multiple_vehicles():
    """Compare multiple vehicles based on form data and return HTML results"""
    try:
        annual_mileage = int(request.form.get('annualMiles', 12000))
        years = int(request.form.get('ownershipYears', 5))
        vehicle_indices = request.form.getlist('vehicle_indices')
        
        if not vehicle_indices:
            return "<div class='alert alert-danger'>Please add at least one vehicle to compare</div>"
        
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
            
            vehicle_dict = {
                'make': make,
                'type': vehicle_type,
                'year': int(year),
                'model': model,
                'fuel_type': fuel_type
            }
            
            vehicle_obj = DepreciationService.get_or_create_vehicle(
                make, model, int(year), fuel_type, vehicle_type
            )
            
            vehicles.append(vehicle_dict)
            vehicle_objects.append(vehicle_obj)
        
        if len(vehicles) < 1:
            return "<div class='alert alert-danger'>No valid vehicles found</div>"
        
        for vehicle in vehicles:
            depreciation = DepreciationService.calculate_depreciation(
                vehicle,
                years=years,
                annual_mileage=annual_mileage
            )
            vehicle_data.append(depreciation)
        
        comparison_data = {
            'vehicles': vehicle_data,
            'count': len(vehicles)
        }
        
        depreciation_chart_url = ChartService.generate_multi_vehicle_chart(
            vehicle_objects, vehicle_data
        )
        
        retention_chart_url = ChartService.generate_multi_vehicle_retention_chart(
            vehicle_objects, vehicle_data
        )
        
        # Use the new service to save the comparison
        charts = {
            'depreciation_chart': depreciation_chart_url,
            'retention_chart': retention_chart_url
        }
        
        parameters = {
            'annual_mileage': annual_mileage,
            'years': years
        }
        
        ComparisonStorageService.save_comparison(
            vehicle_objects, 
            vehicle_data, 
            charts, 
            parameters, 
            current_user if current_user.is_authenticated else None
        )
        
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
