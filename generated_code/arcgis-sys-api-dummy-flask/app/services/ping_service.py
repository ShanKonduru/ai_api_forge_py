from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.ping import Ping
from app.extensions.db import db


class PingService:
    """Service layer for Ping operations"""
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get all ping with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items and pagination info
        """
        try:
            query = Ping.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(Ping, key) and value is not None:
                    query = query.filter(getattr(Ping, key) == value)
            
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
    def get_by_id(ping_id: int) -> Optional[Ping]:
        """
        Get ping by ID
        
        Args:
            ping_id: Ping ID
            
        Returns:
            Ping instance or None
        """
        try:
            return Ping.query.get(ping_id)
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Ping:
        """
        Create new ping
        
        Args:
            data: Ping data
            
        Returns:
            Created Ping instance
        """
        try:
            ping = Ping(**data)
            db.session.add(ping)
            db.session.commit()
            return ping
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def update(ping_id: int, data: Dict[str, Any]) -> Optional[Ping]:
        """
        Update ping
        
        Args:
            ping_id: Ping ID
            data: Updated data
            
        Returns:
            Updated Ping instance or None
        """
        try:
            ping = Ping.query.get(ping_id)
            if ping:
                for key, value in data.items():
                    if hasattr(ping, key):
                        setattr(ping, key, value)
                db.session.commit()
            return ping
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def delete(ping_id: int) -> bool:
        """
        Delete ping
        
        Args:
            ping_id: Ping ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            ping = Ping.query.get(ping_id)
            if ping:
                db.session.delete(ping)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def search(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search ping
        
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
            search_query = Ping.query.filter(
                Ping.name.contains(query)  # Adjust field name as needed
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