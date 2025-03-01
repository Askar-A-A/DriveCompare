from flask import Blueprint

tco_calculator_bp = Blueprint('tco_calculator', __name__, url_prefix='/tco-calculator')

from app.routes.tco_calculator.user_data_input import user_data_input_bp
from app.routes.tco_calculator.depreciation import depreciation_bp

tco_calculator_bp.register_blueprint(user_data_input_bp)
tco_calculator_bp.register_blueprint(depreciation_bp)

