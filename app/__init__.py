from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    register_blueprints(app)
    return app


def register_blueprints(app):    
    from app.routes.main import main_bp
    from app.routes.comparison import comparison_bp
    from app.routes.vehicles import vehicles_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(vehicles_bp)
    return app