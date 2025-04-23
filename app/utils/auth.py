"""
Authorization and role handling utilities for the Car Repair and Sales Tracking application.
"""

from functools import wraps
from flask import abort, redirect, url_for, request
from flask_login import current_user

def requires_role(role):
    """
    Decorator to restrict route access based on user roles.
    
    Args:
        role (str): Required role ('admin', 'manager') 
        
    Example:
        @routes.route('/admin-only')
        @login_required
        @requires_role('admin')
        def admin_only():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
                
            # Admin check
            if role == 'admin' and current_user.role != 'admin':
                abort(403)
                
            # Manager check (admin can also access manager routes)
            if role == 'manager' and current_user.role not in ['manager', 'admin']:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator 