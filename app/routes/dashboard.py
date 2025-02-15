from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def landing():
    return render_template('pages/dashboard.html', title='Dashboard')


