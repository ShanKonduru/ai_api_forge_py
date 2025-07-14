from datetime import datetime
from app.extensions.db import db


class RetrieveSpatialdata(db.Model):
    """RetrieveSpatialdata model"""
    
    __tablename__ = 'retrieve_spatialdata'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize RetrieveSpatialdata instance"""
        super(RetrieveSpatialdata, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<RetrieveSpatialdata {self.id}>'
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': getattr(self, 'id', None),
            'name': getattr(self, 'name', None),
            'created_at': getattr(self, 'created_at', None),
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new RetrieveSpatialdata instance"""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, **kwargs):
        """Update RetrieveSpatialdata instance"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete RetrieveSpatialdata instance"""
        db.session.delete(self)
        db.session.commit()