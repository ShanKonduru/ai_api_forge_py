from flask import Blueprint

# Create API blueprint
bp = Blueprint('api', __name__)

# Import and register resource blueprints
from app.api.v1.v1 import v1_bp
bp.register_blueprint(v1_bp)
from app.api.v1.retrieve_spatialdata import retrieve_spatialdata_bp
bp.register_blueprint(retrieve_spatialdata_bp)
from app.api.v1.mileage_translator import mileage_translator_bp
bp.register_blueprint(mileage_translator_bp)
from app.api.v1.token import token_bp
bp.register_blueprint(token_bp)
from app.api.v1.ping import ping_bp
bp.register_blueprint(ping_bp)

@bp.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'version': 'v1'}, 200