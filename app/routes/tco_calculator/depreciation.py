from flask import Blueprint, request, render_template
from app.models import Vehicle
from app.services.business_logic.depreciation_service import DepreciationService
from app.services.visualization.depreciation_visual import ChartService
from app.database import db

depreciation_bp = Blueprint('depreciation', __name__, url_prefix='/depreciation')

@depreciation_bp.route('/compare-depreciation', methods=['POST'])
def compare_depreciation():
    """Compare vehicle depreciation based on form data and return HTML results"""
    try:
        make1 = request.form.get('make1')
        type1 = request.form.get('type1')
        year1 = request.form.get('year1')
        model1 = request.form.get('model1')
        fuel_type1 = request.form.get('fuelType1')
        
        # Get user inputs for mileage and ownership period
        annual_mileage = int(request.form.get('annualMiles', 12000))
        years = int(request.form.get('ownershipYears', 5))
        
        # Debug the inputs
        print(f"Form data: {request.form}")
        print(f"Annual mileage: {annual_mileage}, Years: {years}")
        
        # Validate primary vehicle inputs
        if not all([make1, year1, model1, fuel_type1]):
            return "<div class='alert alert-danger'>Please select the primary vehicle completely</div>"
        
        # Create vehicle dictionary for the primary vehicle
        vehicle1_data = {
            'make': make1,
            'type': type1,
            'year': int(year1),
            'model': model1,
            'fuel_type': fuel_type1
        }
        
        # Check if we have a second vehicle for comparison
        make2 = request.form.get('make2')
        type2 = request.form.get('type2')
        year2 = request.form.get('year2')
        model2 = request.form.get('model2')
        fuel_type2 = request.form.get('fuelType2')
        
        is_comparison = all([make2, year2, model2, fuel_type2])
        
        # Get the primary vehicle object
        vehicle1 = DepreciationService.get_or_create_vehicle(
            make1, model1, int(year1), fuel_type1, type1
        )
        
        if is_comparison:
            # Create vehicle dictionary for the second vehicle
            vehicle2_data = {
                'make': make2,
                'type': type2,
                'year': int(year2),
                'model': model2,
                'fuel_type': fuel_type2
            }
            
            # Compare depreciation with user-provided values
            comparison_data = DepreciationService.compare_depreciation(
                vehicle1_data, 
                vehicle2_data, 
                years=years,
                annual_mileage=annual_mileage
            )
            
            # Get the second vehicle object
            vehicle2 = DepreciationService.get_or_create_vehicle(
                make2, model2, int(year2), fuel_type2, type2
            )
            
            # Generate comparison charts
            depreciation_chart_url = ChartService.generate_depreciation_chart(
                vehicle1, vehicle2, comparison_data
            )
            
            retention_chart_url = ChartService.generate_retention_chart(
                vehicle1, vehicle2, comparison_data
            )
        else:
            # Calculate depreciation for a single vehicle
            vehicle_depreciation = DepreciationService.calculate_depreciation(
                vehicle1_data,
                years=years,
                annual_mileage=annual_mileage
            )
            
            # Create a simplified comparison data structure for a single vehicle
            comparison_data = {
                'vehicle1': vehicle_depreciation,
                'difference': None
            }
            
            # Generate single vehicle charts
            depreciation_chart_url = ChartService.generate_single_vehicle_chart(
                vehicle1, vehicle_depreciation
            )
            
            retention_chart_url = ChartService.generate_single_vehicle_retention_chart(
                vehicle1, vehicle_depreciation
            )
            
            # Set vehicle2 to None for the template
            vehicle2 = None
        
        # Render results template
        return render_template(
            'partials/tco_results.html',
            vehicle1=vehicle1,
            vehicle2=vehicle2,
            comparison=comparison_data,
            depreciation_chart_url=depreciation_chart_url,
            retention_chart_url=retention_chart_url,
            years=years,
            annual_mileage=annual_mileage,
            is_comparison=is_comparison
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<div class='alert alert-danger'>Error: {str(e)}</div>"
