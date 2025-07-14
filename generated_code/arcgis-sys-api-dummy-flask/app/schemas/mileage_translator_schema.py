from marshmallow import Schema, fields, validate, post_load
from app.models.mileage_translator import MileageTranslator


class MileageTranslatorSchema(Schema):
    """MileageTranslator serialization schema"""
    
    # Define fields based on model
    # Add your specific field definitions here
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        # Include unknown fields
        unknown = 'EXCLUDE'
        # Load instance
        load_instance = True
        # Model class
        model = MileageTranslator
    
    @post_load
    def make_mileage_translator(self, data, **kwargs):
        """Create MileageTranslator instance from validated data"""
        return MileageTranslator(**data)


class MileageTranslatorListSchema(Schema):
    """Schema for MileageTranslator list responses"""
    
    items = fields.List(fields.Nested(MileageTranslatorSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()