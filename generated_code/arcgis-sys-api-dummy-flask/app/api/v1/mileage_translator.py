from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.mileage_translator_service import MileageTranslatorService
from app.schemas.mileage_translator_schema import MileageTranslatorSchema, MileageTranslatorListSchema


mileage_translator_bp = Blueprint('mileage_translator', __name__)
mileage_translator_schema = MileageTranslatorSchema()
mileage_translator_list_schema = MileageTranslatorListSchema()


@mileage_translator_bp.route('/mileage_translator', methods=['POST'])
def post_mileage_translator():
    """
    This API is used to retrieve the MileageTranslator data from ArcGIS
    
    Creates new mileage_translator
    """
    try:
        # Create new mileage_translator
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = mileage_translator_schema.load(request.json)
        mileage_translator = MileageTranslatorService.create(data)
        return jsonify(mileage_translator_schema.dump(mileage_translator)), 201
        
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


