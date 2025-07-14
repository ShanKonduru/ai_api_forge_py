from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.v1 import V1
from app.extensions.db import db


class V1Service:
    """Service layer for V1 operations"""
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get all v1 with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items and pagination info
        """
        try:
            query = V1.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(V1, key) and value is not None:
                    query = query.filter(getattr(V1, key) == value)
            
            # Paginate results
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'items': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def get_by_id(v1_id: int) -> Optional[V1]:
        """
        Get v1 by ID
        
        Args:
            v1_id: V1 ID
            
        Returns:
            V1 instance or None
        """
        try:
            return V1.query.get(v1_id)
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def create(data: Dict[str, Any]) -> V1:
        """
        Create new v1
        
        Args:
            data: V1 data
            
        Returns:
            Created V1 instance
        """
        try:
            v1 = V1(**data)
            db.session.add(v1)
            db.session.commit()
            return v1
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def update(v1_id: int, data: Dict[str, Any]) -> Optional[V1]:
        """
        Update v1
        
        Args:
            v1_id: V1 ID
            data: Updated data
            
        Returns:
            Updated V1 instance or None
        """
        try:
            v1 = V1.query.get(v1_id)
            if v1:
                for key, value in data.items():
                    if hasattr(v1, key):
                        setattr(v1, key, value)
                db.session.commit()
            return v1
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def delete(v1_id: int) -> bool:
        """
        Delete v1
        
        Args:
            v1_id: V1 ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            v1 = V1.query.get(v1_id)
            if v1:
                db.session.delete(v1)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def search(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search v1
        
        Args:
            query: Search query
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with search results and pagination info
        """
        try:
            # Implement search logic based on your model fields
            # This is a basic example - customize based on your needs
            search_query = V1.query.filter(
                V1.name.contains(query)  # Adjust field name as needed
            )
            
            pagination = search_query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'items': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages,
                'query': query
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")