from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.retrieve_spatialdata_service import RetrieveSpatialdataService
from app.schemas.retrieve_spatialdata_schema import RetrieveSpatialdataSchema, RetrieveSpatialdataListSchema


retrieve_spatialdata_bp = Blueprint('retrieve_spatialdata', __name__)
retrieve_spatialdata_schema = RetrieveSpatialdataSchema()
retrieve_spatialdata_list_schema = RetrieveSpatialdataListSchema()


@retrieve_spatialdata_bp.route('/retrieve_spatialdata', methods=['POST'])
def post_retrieve_spatialdata():
    """
    This API is used to retrieve the spatial data from ArcGIS
    
    Creates new retrieve_spatialdata
    """
    try:
        # Create new retrieve_spatialdata
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = retrieve_spatialdata_schema.load(request.json)
        retrieve_spatialdata = RetrieveSpatialdataService.create(data)
        return jsonify(retrieve_spatialdata_schema.dump(retrieve_spatialdata)), 201
        
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


