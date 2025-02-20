from flask import Blueprint, jsonify
from app.services.vehicle_api import NHTSAService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/makes')
def get_makes():
    """Get all makes"""
    print("4. /api/makes route handler called")
    makes = NHTSAService.get_makes()
    print("7. Received makes from NHTSAService:", makes[:2] if makes else "No makes received")
    return jsonify(makes)

@api_bp.route('/years/<string:make>') 
def get_years(make):
    """Get available years for a specific make"""
    years = NHTSAService.get_years_for_make(make)
    return jsonify(years)

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
