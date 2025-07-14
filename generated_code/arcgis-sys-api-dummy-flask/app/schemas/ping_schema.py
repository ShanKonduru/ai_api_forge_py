from marshmallow import Schema, fields, validate, post_load
from app.models.ping import Ping


class PingSchema(Schema):
    """Ping serialization schema"""
    
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
        model = Ping
    
    @post_load
    def make_ping(self, data, **kwargs):
        """Create Ping instance from validated data"""
        return Ping(**data)


class PingListSchema(Schema):
    """Schema for Ping list responses"""
    
    items = fields.List(fields.Nested(PingSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()