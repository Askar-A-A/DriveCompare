from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.routes.api.vehicles import vehicles_api_bp

api_bp.register_blueprint(vehicles_api_bp)

