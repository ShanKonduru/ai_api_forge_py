from datetime import datetime
from app.extensions.db import db


class Token(db.Model):
    """Token model"""
    
    __tablename__ = 'token'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize Token instance"""
        super(Token, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Token {self.id}>'
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': getattr(self, 'id', None),
            'name': getattr(self, 'name', None),
            'created_at': getattr(self, 'created_at', None),
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new Token instance"""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, **kwargs):
        """Update Token instance"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete Token instance"""
        db.session.delete(self)
        db.session.commit()