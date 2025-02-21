from flask import Blueprint, jsonify
from app.services.vehicle_api import NHTSAService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/makes')
def get_makes():
    makes = NHTSAService.get_makes()
    # Debug: Print total number and sample of makes
    print(f"Total makes received: {len(makes)}")
    print("Sample of first 10 makes:", [make['Make_Name'] for make in makes[:10]])
    # Option 1: If we find the data is correct but want to filter popular makes
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
    
    # Filter to only popular makes
    filtered_makes = [
        make for make in makes 
        if make.get('Make_Name', '').upper() in POPULAR_MAKES
    ]
    print(f"Filtered makes count: {len(filtered_makes)}")
    return jsonify(filtered_makes)


@api_bp.route('/vehicle-types/<string:make>')
def get_vehicle_types(make):
    """Get all vehicle types for a specific make"""
    vehicle_types = NHTSAService.get_vehicle_types(make)
    if not vehicle_types:
        return jsonify([])
    return jsonify(vehicle_types)


@api_bp.route('/models/<string:make>/<int:year>/<string:vehicle_type>')
def get_models(make, year, vehicle_type):
    """Get all models for a specific make and year"""
    models = NHTSAService.get_models(make, year, vehicle_type)
    return jsonify(models)

