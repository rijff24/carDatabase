"""
Error handling utilities for the Car Repair and Sales Tracking application.

This module provides:
1. Custom exception classes for different types of errors
2. Error handler functions for common HTTP errors
3. Utility functions for error handling
"""

from flask import jsonify, render_template, request, current_app
from werkzeug.exceptions import HTTPException, NotFound
import traceback
import sys

class AppError(Exception):
    """Base exception class for application-specific errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert error to dictionary format for JSON responses."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, message, field=None, payload=None):
        super().__init__(message, status_code=400, payload=payload)
        self.field = field

class DatabaseError(AppError):
    """Raised when database operations fail."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=500, payload=payload)

class AuthenticationError(AppError):
    """Raised when authentication fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(AppError):
    """Raised when authorization fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

def register_error_handlers(app, db):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def handle_not_found_error(error):
        """Handle 404 errors."""
        app.logger.warning(f"404 Error: {request.path}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            response = jsonify({
                'message': "Resource not found",
                'status_code': 404
            })
            response.status_code = 404
            return response
        
        return render_template('errors/404.html'), 404

    @app.errorhandler(NotFoundError)
    def handle_app_not_found_error(error):
        """Handle application NotFoundError."""
        app.logger.warning(f"NotFoundError: {error.message}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            response = jsonify(error.to_dict())
            response.status_code = 404
            return response
        
        return render_template('errors/404.html', message=error.message), 404
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle application-specific errors."""
        # Log the error
        app.logger.error(f"AppError: {error.message}")
        
        # Check if request is expecting JSON
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        
        # Otherwise return HTML response
        return render_template(f'errors/{error.status_code}.html', 
                              message=error.message), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle HTTP errors."""
        app.logger.warning(f"HTTP Exception: {error.code} - {error.description}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            response = jsonify({
                'message': error.description,
                'status_code': error.code
            })
            response.status_code = error.code
            return response
        
        # Render HTML template for the error code if it exists
        try:
            return render_template(f'errors/{error.code}.html'), error.code
        except:
            return render_template('errors/generic.html', 
                                  error_code=error.code, 
                                  error_message=error.description), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle unexpected errors."""
        # Log the full error with traceback for debugging
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
        app.logger.error(f"Unhandled Exception: {str(error)}")
        app.logger.error(''.join(error_details))
        
        # Print to stderr in case logger isn't catching it
        print(f"ERROR: {str(error)}", file=sys.stderr)
        print(''.join(error_details), file=sys.stderr)
        
        # Roll back any pending database transactions
        if hasattr(app, 'extensions') and 'sqlalchemy' in app.extensions:
            db.session.rollback()
        
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            response = jsonify({
                'message': 'An unexpected error occurred',
                'status_code': 500,
                'error': str(error) if app.config.get('DEBUG', False) else None
            })
            response.status_code = 500
            return response
        
        # For HTML requests, render a 500 error page
        return render_template('errors/500.html', 
                              error=str(error) if app.config.get('DEBUG', False) else None), 500

def format_error_message(error):
    """Format error message for display to users."""
    if isinstance(error, ValidationError):
        if error.field:
            return f"Error in {error.field}: {error.message}"
    return error.message

def handle_api_error(error, db):
    """Handle errors in API endpoints."""
    if isinstance(error, AppError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    # Handle unexpected errors
    if hasattr(db, 'session'):
        db.session.rollback()
    response = jsonify({
        'message': 'An unexpected error occurred',
        'status_code': 500
    })
    response.status_code = 500
    return response 