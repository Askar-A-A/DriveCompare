from flask import Blueprint, jsonify
from app.services.vehicle_api import NHTSAService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/makes/<int:year>')
def get_makes(year):
    """Get all makes for a specific year"""
    try:
        makes = NHTSAService.get_makes(year)
        if makes:
            return jsonify(makes)
        return jsonify({'error': 'No makes found for this year'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/models/<string:make>/<int:year>')
def get_models(make, year):
    """Get all models for a specific make and year"""
    try:
        models = NHTSAService.get_models(make, year)
        if models:
            return jsonify(models)
        return jsonify({'error': 'No models found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/vehicle/<string:vin>')
def get_vehicle_info(vin):
    """Get detailed vehicle information by VIN"""
    try:
        vehicle_info = NHTSAService.get_vehicle_info(vin)
        if vehicle_info:
            return jsonify(vehicle_info)
        return jsonify({'error': 'Vehicle not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
