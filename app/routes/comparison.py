from flask import Blueprint, render_template

comparison_bp = Blueprint('comparison', __name__, url_prefix='/comparison')

@comparison_bp.route('/')
def landing():
    return render_template('pages/comparison.html', title='Comparison')


