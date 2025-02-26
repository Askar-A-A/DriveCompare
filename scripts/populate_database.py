import sys
import os
from typing import List, Dict
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Vehicle
from app.services.vehicle_api import NHTSAService
from app.database import db

# Popular makes set
POPULAR_MAKES = {
    # Japanese
    'HONDA', 'TOYOTA', 'NISSAN', 'SUBARU', 'MAZDA', 'LEXUS', 'INFINITI', 'ACURA', 'MITSUBISHI',
    'SCION', 'ISUZU', 'SUZUKI', 'DAIHATSU',
    # American
    'FORD', 'CHEVROLET', 'JEEP', 'CHRYSLER', 'DODGE', 'RAM', 'CADILLAC', 'BUICK', 'GMC', 
    'LINCOLN', 'TESLA', 'HUMMER', 'PONTIAC', 'SATURN', 'MERCURY',
    # German
    'BMW', 'MERCEDES-BENZ', 'AUDI', 'VOLKSWAGEN', 'PORSCHE', 'MINI', 'OPEL', 
    'SMART', 'MAYBACH', 'ALPINA',
    # Korean
    'HYUNDAI', 'KIA', 'GENESIS', 'SSANGYONG', 'DAEWOO',
    # Chinese
    'BYD', 'GEELY', 'GREAT WALL', 'NIO', 'XPENG', 'LI AUTO', 'MG', 'POLESTAR',
    # Swedish
    'VOLVO', 'SAAB', 'KOENIGSEGG',
    # Italian
    'ALFA ROMEO', 'MASERATI', 'FIAT', 'FERRARI', 'LAMBORGHINI', 'LANCIA', 'PAGANI',
    # British
    'JAGUAR', 'LAND ROVER', 'BENTLEY', 'ROLLS-ROYCE', 'ASTON MARTIN', 'LOTUS', 'MCLAREN',
    'TRIUMPH', 'MG',
    # French
    'PEUGEOT', 'RENAULT', 'CITROEN', 'DS', 'BUGATTI', 'ALPINE',
    # Other European
    'SKODA', 'SEAT', 'RIMAC',
    # Indian
    'TATA', 'MAHINDRA',
    # Malaysian
    'PROTON', 'PERODUA',
    # Vietnamese
    'VINFAST',
    # Other Luxury/Performance
    'KOENIGSEGG', 'PININFARINA', 'ZENVO', 'LUCID', 'RIVIAN'
}

def populate_vehicles():
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get all makes first
        print("Fetching makes...")
        makes = NHTSAService.get_makes()
        
        # Filter makes
        makes = [make for make in makes if make.get('Make_Name', '').upper() in POPULAR_MAKES]
        print(f"Found {len(makes)} popular makes to process")
        
        # Years to consider (adjust as needed)
        years = range(2020, 2025)  # Last 5 years
        
        total_vehicles = 0
        
        for make_data in makes:
            make = make_data.get('Make_Name', '').upper()
            print(f"\nProcessing make: {make}")
            
            # Get vehicle types for this make
            vehicle_types = NHTSAService.get_vehicle_types(make)
            
            for vehicle_type_data in vehicle_types:
                vehicle_type = vehicle_type_data.get('VehicleTypeName', '')
                print(f"  Processing vehicle type: {vehicle_type}")
                
                for year in years:
                    print(f"    Processing year: {year}")
                    
                    # Get models for this make, year, and vehicle type
                    models = NHTSAService.get_models(make, year, vehicle_type)
                    
                    for model_data in models:
                        model = model_data.get('Model_Name', '')
                        
                        # Check if vehicle already exists
                        existing_vehicle = Vehicle.query.filter_by(
                            make=make,
                            model=model,
                            year=year,
                            type=vehicle_type
                        ).first()
                        
                        if not existing_vehicle:
                            # Create new vehicle
                            vehicle = Vehicle(
                                make=make,
                                model=model,
                                year=year,
                                type=vehicle_type,
                                created_at=datetime.utcnow()
                            )
                            
                            db.session.add(vehicle)
                            total_vehicles += 1
                            
                            # Commit every 100 vehicles to avoid memory issues
                            if total_vehicles % 100 == 0:
                                print(f"    Committing batch... Total vehicles so far: {total_vehicles}")
                                db.session.commit()
        
        # Final commit for remaining vehicles
        db.session.commit()
        print(f"\nFinished! Total vehicles added to database: {total_vehicles}")

if __name__ == "__main__":
    populate_vehicles()
