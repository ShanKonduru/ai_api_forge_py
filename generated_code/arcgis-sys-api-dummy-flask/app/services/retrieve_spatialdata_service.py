from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.retrieve_spatialdata import RetrieveSpatialdata
from app.extensions.db import db


class RetrieveSpatialdataService:
    """Service layer for RetrieveSpatialdata operations"""
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get all retrieve_spatialdata with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items and pagination info
        """
        try:
            query = RetrieveSpatialdata.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(RetrieveSpatialdata, key) and value is not None:
                    query = query.filter(getattr(RetrieveSpatialdata, key) == value)
            
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
    def get_by_id(retrieve_spatialdata_id: int) -> Optional[RetrieveSpatialdata]:
        """
        Get retrieve_spatialdata by ID
        
        Args:
            retrieve_spatialdata_id: RetrieveSpatialdata ID
            
        Returns:
            RetrieveSpatialdata instance or None
        """
        try:
            return RetrieveSpatialdata.query.get(retrieve_spatialdata_id)
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def create(data: Dict[str, Any]) -> RetrieveSpatialdata:
        """
        Create new retrieve_spatialdata
        
        Args:
            data: RetrieveSpatialdata data
            
        Returns:
            Created RetrieveSpatialdata instance
        """
        try:
            retrieve_spatialdata = RetrieveSpatialdata(**data)
            db.session.add(retrieve_spatialdata)
            db.session.commit()
            return retrieve_spatialdata
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def update(retrieve_spatialdata_id: int, data: Dict[str, Any]) -> Optional[RetrieveSpatialdata]:
        """
        Update retrieve_spatialdata
        
        Args:
            retrieve_spatialdata_id: RetrieveSpatialdata ID
            data: Updated data
            
        Returns:
            Updated RetrieveSpatialdata instance or None
        """
        try:
            retrieve_spatialdata = RetrieveSpatialdata.query.get(retrieve_spatialdata_id)
            if retrieve_spatialdata:
                for key, value in data.items():
                    if hasattr(retrieve_spatialdata, key):
                        setattr(retrieve_spatialdata, key, value)
                db.session.commit()
            return retrieve_spatialdata
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def delete(retrieve_spatialdata_id: int) -> bool:
        """
        Delete retrieve_spatialdata
        
        Args:
            retrieve_spatialdata_id: RetrieveSpatialdata ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            retrieve_spatialdata = RetrieveSpatialdata.query.get(retrieve_spatialdata_id)
            if retrieve_spatialdata:
                db.session.delete(retrieve_spatialdata)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def search(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search retrieve_spatialdata
        
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
            search_query = RetrieveSpatialdata.query.filter(
                RetrieveSpatialdata.name.contains(query)  # Adjust field name as needed
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