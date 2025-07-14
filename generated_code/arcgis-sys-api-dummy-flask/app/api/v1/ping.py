from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.ping_service import PingService
from app.schemas.ping_schema import PingSchema, PingListSchema


ping_bp = Blueprint('ping', __name__)
ping_schema = PingSchema()
ping_list_schema = PingListSchema()


@ping_bp.route('/ping', methods=['GET'])
def get_ping():
    """
    Return a standard response.
    
    Returns: ping data
    """
    try:
        # Get all ping with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Extract query parameters as filters
        filters = {}
        for key, value in request.args.items():
            if key not in ['page', 'per_page']:
                filters[key] = value
        
        result = PingService.get_all(page=page, per_page=per_page, **filters)
        return jsonify(ping_list_schema.dump(result)), 200
        
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


