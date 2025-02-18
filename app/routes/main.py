from flask import Blueprint, render_template, jsonify
from app.database import db
from app.models import Vehicle  

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('pages/home.html', title='Home')

@main_bp.route('/test-db')
def test_db():
    try:
        # Test 1: Basic database connection
        db.session.execute('SELECT 1')
        
        # Test 2: Create a test vehicle
        test_vehicle = Vehicle(
            make='Tesla',
            model='Model 3',
            year=2024,
            type='EV'
        )
        db.session.add(test_vehicle)
        db.session.commit()
        
        # Test 3: Query the vehicle back
        vehicle = Vehicle.query.filter_by(make='Tesla').first()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful!',
            'test_vehicle': vehicle.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500 
