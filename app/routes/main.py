from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('pages/home.html', title='Home')


