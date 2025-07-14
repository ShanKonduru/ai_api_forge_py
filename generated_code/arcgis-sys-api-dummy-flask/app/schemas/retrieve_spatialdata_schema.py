from marshmallow import Schema, fields, validate, post_load
from app.models.retrieve_spatialdata import RetrieveSpatialdata


class RetrieveSpatialdataSchema(Schema):
    """RetrieveSpatialdata serialization schema"""
    
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
        model = RetrieveSpatialdata
    
    @post_load
    def make_retrieve_spatialdata(self, data, **kwargs):
        """Create RetrieveSpatialdata instance from validated data"""
        return RetrieveSpatialdata(**data)


class RetrieveSpatialdataListSchema(Schema):
    """Schema for RetrieveSpatialdata list responses"""
    
    items = fields.List(fields.Nested(RetrieveSpatialdataSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()