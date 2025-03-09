from app.models import TCOComparison, Vehicle
from app.database import db
from flask_login import current_user

class ComparisonStorageService:
    @staticmethod
    def save_comparison(vehicle_objects, vehicle_data, charts, parameters, user=None):
        """
        Save TCO comparison data to database
        
        Args:
            vehicle_objects: List of Vehicle model objects
            vehicle_data: List of dictionaries with calculated depreciation/cost data
            charts: Dictionary with chart URLs (depreciation_chart, retention_chart)
            parameters: Dictionary with comparison parameters (years, annual_mileage)
            user: Current user object (optional)
            
        Returns:
            TCOComparison: The saved comparison record
        """
        # Create the comparison record with primary vehicle
        primary_vehicle = vehicle_objects[0]
        comparison_record = TCOComparison(
            vehicle1_id=primary_vehicle.id,
            vehicle1_make=primary_vehicle.make,
            vehicle1_model=primary_vehicle.model,
            vehicle1_year=primary_vehicle.year,
            vehicle1_fuel_type=primary_vehicle.fuel_type,
            vehicle1_type=primary_vehicle.type,
            
            annual_mileage=parameters.get('annual_mileage', 12000),
            ownership_years=parameters.get('years', 5),
            
            is_comparison=len(vehicle_objects) > 1
        )
        
        # Add second vehicle if this is a comparison
        if len(vehicle_objects) > 1:
            second_vehicle = vehicle_objects[1]
            comparison_record.vehicle2_id = second_vehicle.id
            comparison_record.vehicle2_make = second_vehicle.make
            comparison_record.vehicle2_model = second_vehicle.model
            comparison_record.vehicle2_year = second_vehicle.year
            comparison_record.vehicle2_fuel_type = second_vehicle.fuel_type
            comparison_record.vehicle2_type = second_vehicle.type
        
        # Prepare the comparison data to store
        comparison_data_to_store = {}
        
        for i, (vehicle_obj, vehicle_depr) in enumerate(zip(vehicle_objects, vehicle_data)):
            vehicle_key = f'vehicle{i+1}'
            comparison_data_to_store[vehicle_key] = {
                'initial_cost': vehicle_depr.get('initial_price', 0),
                'depreciation_cost': vehicle_depr.get('total_depreciation', 0),
                'fuel_cost': 0,
                'maintenance_cost': 0,
                'insurance_cost': 0,
                'total_cost': vehicle_depr.get('total_depreciation', 0),
                'resale_value': vehicle_depr.get('final_value', 0)
            }
        
        # Store the comparison data
        comparison_record.set_comparison_data(comparison_data_to_store)
        
        # Add chart URLs
        comparison_record.depreciation_chart = charts.get('depreciation_chart')
        comparison_record.retention_chart = charts.get('retention_chart')
        
        # Associate with user if authenticated
        if user:
            comparison_record.user_id = user.id
        
        # Save to database
        db.session.add(comparison_record)
        db.session.commit()
        
        return comparison_record
