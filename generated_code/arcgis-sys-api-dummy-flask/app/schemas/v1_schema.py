from marshmallow import Schema, fields, validate, post_load
from app.models.v1 import V1


class V1Schema(Schema):
    """V1 serialization schema"""
    
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
        model = V1
    
    @post_load
    def make_v1(self, data, **kwargs):
        """Create V1 instance from validated data"""
        return V1(**data)


class V1ListSchema(Schema):
    """Schema for V1 list responses"""
    
    items = fields.List(fields.Nested(V1Schema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()