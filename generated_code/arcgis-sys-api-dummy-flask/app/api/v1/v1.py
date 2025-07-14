from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services.v1_service import V1Service
from app.schemas.v1_schema import V1Schema, V1ListSchema


v1_bp = Blueprint('v1', __name__)
v1_schema = V1Schema()
v1_list_schema = V1ListSchema()


