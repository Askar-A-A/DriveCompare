from flask import Blueprint, request, render_template
from app.models import Vehicle
from app.services.business_logic.depreciation_service import DepreciationService
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
        
        make2 = request.form.get('make2')
        type2 = request.form.get('type2')
        year2 = request.form.get('year2')
        model2 = request.form.get('model2')
        
        annual_mileage = int(request.form.get('annualMiles', 12000))
        years = int(request.form.get('ownershipYears', 5))
        
        # Validate inputs
        if not all([make1, type1, year1, model1, make2, type2, year2, model2]):
            return "<div class='alert alert-danger'>Please select both vehicles completely</div>"
        
        # Get vehicles from database
        vehicle1 = Vehicle.query.filter_by(
            make=make1, 
            type=type1, 
            year=year1, 
            model=model1
        ).first()
        
        vehicle2 = Vehicle.query.filter_by(
            make=make2, 
            type=type2, 
            year=year2, 
            model=model2
        ).first()
        
        if not vehicle1 or not vehicle2:
            return "<div class='alert alert-danger'>One or both vehicles could not be found</div>"
        
        # Compare depreciation
        comparison_data = DepreciationService.compare_depreciation(
            vehicle1, 
            vehicle2, 
            years=years, 
            annual_mileage=annual_mileage
        )
        
        # Render results template
        return render_template(
            'partials/tco_results.html',
            vehicle1=vehicle1,
            vehicle2=vehicle2,
            comparison=comparison_data
        )
        
    except Exception as e:
        return f"<div class='alert alert-danger'>Error: {str(e)}</div>"
