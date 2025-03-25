"""
Helper functions for the Car Repair and Sales Tracking application.

This module provides utility functions for common operations throughout the application.
"""

from flask import current_app
from app.utils.errors import NotFoundError
from app import db

def safe_get_or_404(model_class, id, description=None):
    """
    Safely retrieve a resource by ID or raise a proper 404 error.
    This is a wrapper around SQLAlchemy's get_or_404 to provide consistent 
    error handling with our error system.
    
    Args:
        model_class: SQLAlchemy model class
        id: The ID to look up
        description: Custom error message, defaults to "Resource not found"
        
    Returns:
        The found object
        
    Raises:
        NotFoundError: If the object is not found
    """
    # Extract the model name and primary key from the model class
    model_name = model_class.__tablename__
    primary_key = model_class.__mapper__.primary_key[0].name
    
    # Build a query to get the record
    result = db.session.execute(
        db.select(model_class).filter(getattr(model_class, primary_key) == id)
    ).scalar_one_or_none()
    
    if result is None:
        if description is None:
            description = f"{model_name.capitalize()} with ID {id} not found"
        raise NotFoundError(description)
    
    return result 