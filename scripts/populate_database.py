import sys
import os
from typing import List, Dict, Tuple
from datetime import datetime
import time
from tqdm import tqdm  # For progress bars

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Vehicle
from app.services.data.vehicle_api import EPAFuelEconomyService
from app.database import db

# Popular makes set - we'll keep this to filter the makes
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

def setup_database():
    """Ensure the database schema is up to date"""
    app = create_app()
    with app.app_context():
        print("Setting up database schema...")
        # Drop existing tables if they exist
        db.drop_all()
        # Create all tables based on current models
        db.create_all()
        print("Database schema created successfully.")

def populate_vehicles():
    """Populate the database with vehicles from the EPA FuelEconomy.gov API"""
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Starting database population with EPA FuelEconomy.gov data...")
        
        # Get all years
        print("Fetching available years...")
        years = [year[0] for year in EPAFuelEconomyService.get_years()]
        years = [year for year in years if year >= 2025]  # Filter to years 2000 and newer
        print(f"Found {len(years)} years to process")
        
        total_vehicles = 0
        
        # Process each year
        for year in tqdm(years, desc="Processing years"):
            # Get makes for this year
            makes_data = EPAFuelEconomyService.get_makes(year)
            makes = [make[0] for make in makes_data]
            
            # Filter to popular makes
            makes = [make for make in makes if make.upper() in POPULAR_MAKES]
            
            # Process each make
            for make in tqdm(makes, desc=f"Processing makes for {year}", leave=False):
                # Get models for this make and year
                models_data = EPAFuelEconomyService.get_models(make, year)
                models = [model[0] for model in models_data]
                
                # Process each model
                for model in models:
                    try:
                        # Get fuel types for this model
                        fuel_types = EPAFuelEconomyService.get_fuel_types(make, model, year)
                        fuel_types = [ft[0] for ft in fuel_types]
                        
                        # If no fuel types found, use a default
                        if not fuel_types:
                            fuel_types = ['Gasoline']
                        
                        # Get vehicle types (EPA doesn't provide this, so we'll use a simplified approach)
                        # We'll determine type based on the model name or use a default
                        vehicle_type = determine_vehicle_type(model)
                        
                        # Add a vehicle entry for each fuel type
                        for fuel_type in fuel_types:
                            # Create new vehicle
                            vehicle = Vehicle(
                                make=make,
                                model=model,
                                year=year,
                                type=vehicle_type,
                                fuel_type=fuel_type,
                                created_at=datetime.utcnow()
                            )
                            
                            db.session.add(vehicle)
                            total_vehicles += 1
                            
                            # Commit every 100 vehicles to avoid memory issues
                            if total_vehicles % 100 == 0:
                                print(f"Committing batch... Total vehicles so far: {total_vehicles}")
                                db.session.commit()
                    except Exception as e:
                        print(f"Error processing model {model} for {make} {year}: {e}")
                        continue
                
                # Add a small delay to avoid overwhelming the API
                time.sleep(0.1)
        
        # Final commit for remaining vehicles
        db.session.commit()
        print(f"\nFinished! Total vehicles added to database: {total_vehicles}")

def determine_vehicle_type(model_name: str) -> str:
    """
    Determine vehicle type based on model name.
    This is a simplified approach since EPA doesn't provide vehicle type data.
    """
    model_lower = model_name.lower()
    
    # Check for SUVs
    if any(term in model_lower for term in ['suv', 'crossover', 'explorer', 'escape', 'expedition', 'tahoe', 'suburban', 'equinox']):
        return 'SUV'
    
    # Check for trucks
    if any(term in model_lower for term in ['truck', 'pickup', 'silverado', 'f-150', 'ram', 'ranger', 'tacoma', 'tundra', 'colorado']):
        return 'Truck'
    
    # Check for vans
    if any(term in model_lower for term in ['van', 'caravan', 'sienna', 'odyssey', 'pacifica']):
        return 'Van'
    
    # Check for coupes
    if any(term in model_lower for term in ['coupe', 'mustang', 'camaro', 'challenger', 'corvette']):
        return 'Coupe'
    
    # Check for convertibles
    if any(term in model_lower for term in ['convertible', 'cabriolet', 'spyder', 'spider']):
        return 'Convertible'
    
    # Check for hatchbacks
    if any(term in model_lower for term in ['hatchback', 'golf', 'civic hatch', 'fit', 'yaris']):
        return 'Hatchback'
    
    # Check for wagons
    if any(term in model_lower for term in ['wagon', 'estate', 'touring', 'outback']):
        return 'Wagon'
    
    # Default to sedan if no other type matches
    return 'Sedan'

if __name__ == "__main__":
    # First set up the database schema
    setup_database()
    # Then populate the vehicles
    populate_vehicles()
