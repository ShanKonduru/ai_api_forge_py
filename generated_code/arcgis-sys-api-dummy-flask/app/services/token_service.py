from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.token import Token
from app.extensions.db import db


class TokenService:
    """Service layer for Token operations"""
    
    @staticmethod
    def get_all(page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get all token with pagination
        
        Args:
            page: Page number
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items and pagination info
        """
        try:
            query = Token.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(Token, key) and value is not None:
                    query = query.filter(getattr(Token, key) == value)
            
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
    def get_by_id(token_id: int) -> Optional[Token]:
        """
        Get token by ID
        
        Args:
            token_id: Token ID
            
        Returns:
            Token instance or None
        """
        try:
            return Token.query.get(token_id)
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Token:
        """
        Create new token
        
        Args:
            data: Token data
            
        Returns:
            Created Token instance
        """
        try:
            token = Token(**data)
            db.session.add(token)
            db.session.commit()
            return token
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def update(token_id: int, data: Dict[str, Any]) -> Optional[Token]:
        """
        Update token
        
        Args:
            token_id: Token ID
            data: Updated data
            
        Returns:
            Updated Token instance or None
        """
        try:
            token = Token.query.get(token_id)
            if token:
                for key, value in data.items():
                    if hasattr(token, key):
                        setattr(token, key, value)
                db.session.commit()
            return token
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def delete(token_id: int) -> bool:
        """
        Delete token
        
        Args:
            token_id: Token ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            token = Token.query.get(token_id)
            if token:
                db.session.delete(token)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    @staticmethod
    def search(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Search token
        
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
            search_query = Token.query.filter(
                Token.name.contains(query)  # Adjust field name as needed
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