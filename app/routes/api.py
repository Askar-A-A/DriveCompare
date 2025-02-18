from flask import Blueprint, jsonify
from app.services.vehicle_api import NHTSAService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/makes/<int:year>')
def get_makes(year):
    """Get all makes for a specific year"""
    makes = NHTSAService.get_makes(year)
    return jsonify(makes)

@api_bp.route('/models/<string:make>/<int:year>')
def get_models(make, year):
    """Get all models for a specific make and year"""
    models = NHTSAService.get_models(make, year)
    return jsonify(models)

@api_bp.route('/vehicle/<string:vin>')
def get_vehicle_info(vin):
    """Get detailed vehicle information by VIN"""
    vehicle_info = NHTSAService.get_vehicle_info(vin)
    return jsonify(vehicle_info)
