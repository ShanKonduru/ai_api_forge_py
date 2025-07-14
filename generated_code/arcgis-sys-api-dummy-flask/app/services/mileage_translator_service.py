from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.mileage_translator import MileageTranslator
from app.extensions.db import db


class MileageTranslatorService:
    """Service layer for MileageTranslator operations"""
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get all mileage_translator with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items and pagination info
        """
        try:
            query = MileageTranslator.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(MileageTranslator, key) and value is not None:
                    query = query.filter(getattr(MileageTranslator, key) == value)
            
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
    def get_by_id(mileage_translator_id: int) -> Optional[MileageTranslator]:
        """
        Get mileage_translator by ID
        
        Args:
            mileage_translator_id: MileageTranslator ID
            
        Returns:
            MileageTranslator instance or None
        """
        try:
            return MileageTranslator.query.get(mileage_translator_id)
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def create(data: Dict[str, Any]) -> MileageTranslator:
        """
        Create new mileage_translator
        
        Args:
            data: MileageTranslator data
            
        Returns:
            Created MileageTranslator instance
        """
        try:
            mileage_translator = MileageTranslator(**data)
            db.session.add(mileage_translator)
            db.session.commit()
            return mileage_translator
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def update(mileage_translator_id: int, data: Dict[str, Any]) -> Optional[MileageTranslator]:
        """
        Update mileage_translator
        
        Args:
            mileage_translator_id: MileageTranslator ID
            data: Updated data
            
        Returns:
            Updated MileageTranslator instance or None
        """
        try:
            mileage_translator = MileageTranslator.query.get(mileage_translator_id)
            if mileage_translator:
                for key, value in data.items():
                    if hasattr(mileage_translator, key):
                        setattr(mileage_translator, key, value)
                db.session.commit()
            return mileage_translator
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def delete(mileage_translator_id: int) -> bool:
        """
        Delete mileage_translator
        
        Args:
            mileage_translator_id: MileageTranslator ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            mileage_translator = MileageTranslator.query.get(mileage_translator_id)
            if mileage_translator:
                db.session.delete(mileage_translator)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def search(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search mileage_translator
        
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
            search_query = MileageTranslator.query.filter(
                MileageTranslator.name.contains(query)  # Adjust field name as needed
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