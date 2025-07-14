from datetime import datetime
from app.extensions.db import db


class Ping(db.Model):
    """Ping model"""
    
    __tablename__ = 'ping'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize Ping instance"""
        super(Ping, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<Ping {self.id}>'
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': getattr(self, 'id', None),
            'name': getattr(self, 'name', None),
            'created_at': getattr(self, 'created_at', None),
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new Ping instance"""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, **kwargs):
        """Update Ping instance"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete Ping instance"""
        db.session.delete(self)
        db.session.commit()