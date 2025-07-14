from marshmallow import Schema, fields, validate, post_load
from app.models.token import Token


class TokenSchema(Schema):
    """Token serialization schema"""
    
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
        model = Token
    
    @post_load
    def make_token(self, data, **kwargs):
        """Create Token instance from validated data"""
        return Token(**data)


class TokenListSchema(Schema):
    """Schema for Token list responses"""
    
    items = fields.List(fields.Nested(TokenSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()