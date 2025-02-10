from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    # db.init_app(app)  # Commented until we add database
    
    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app