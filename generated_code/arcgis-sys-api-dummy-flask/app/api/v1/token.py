from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.token_service import TokenService
from app.schemas.token_schema import TokenSchema, TokenListSchema


token_bp = Blueprint('token', __name__)
token_schema = TokenSchema()
token_list_schema = TokenListSchema()


@token_bp.route('/token', methods=['GET'])
def get_token():
    """
    Return a token response.
    
    Returns: token data
    """
    try:
        # Get all token with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Extract query parameters as filters
        filters = {}
        for key, value in request.args.items():
            if key not in ['page', 'per_page']:
                filters[key] = value
        
        result = TokenService.get_all(page=page, per_page=per_page, **filters)
        return jsonify(token_list_schema.dump(result)), 200
        
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


