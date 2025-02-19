from app.models import Vehicle
from app.services.vehicle_api import NHTSAService

class VehicleFactory:
    @staticmethod
    def create_vehicle(make: str, model: str, year: int, vehicle_type: str) -> Vehicle:
        """Create a vehicle with data from NHTSA API"""
        # Get vehicle details from NHTSA
        if vehicle_type == 'EV':
            vehicle_data = NHTSAService.get_ev_details(make, model, year)
        else:
            vehicle_data = NHTSAService.get_fuel_types(make, model, year)
        
        # Create new vehicle
        vehicle = Vehicle(
            make=make,
            model=model,
            year=year,
            type=vehicle_type
        )
        
        # Update with NHTSA data if available
        if vehicle_data:
            vehicle.fuel_type = vehicle_data.get('FuelTypePrimary')
            vehicle.drive_type = vehicle_data.get('DriveType')
            
        return vehicle