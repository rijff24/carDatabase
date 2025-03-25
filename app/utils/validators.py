"""
Validation utilities for the Car Repair and Sales Tracking application.

This module provides:
1. Parameter validation decorators
2. Type conversion utilities
3. Common validation functions
"""

from functools import wraps
from flask import request, jsonify, abort
from app.utils.errors import ValidationError, NotFoundError
from datetime import datetime
import re

def validate_params(**validations):
    """
    Decorator for validating route parameters.
    
    Args:
        **validations: Dictionary of parameter names and their validation rules.
                     Each rule can be a tuple of (type, required, default) or
                     (type, required, default, custom_validator)
                     where custom_validator is a function that returns True/False.
    
    Example:
        @validate_params(
            year=(int, True, None),
            month=(int, False, None),
            period=(str, False, 'monthly', lambda x: x in ['daily', 'weekly', 'monthly'])
        )
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []
            validated_params = {}
            
            # Check for route params (e.g., /resource/<id>) that should be valid integers
            for param_name, rule in validations.items():
                # Check if the parameter is in the URL path and should be an integer
                if param_name in kwargs and isinstance(rule, tuple) and len(rule) > 0 and rule[0] == int:
                    try:
                        # Try to convert the URL parameter to an integer
                        int(kwargs[param_name])
                    except (ValueError, TypeError):
                        # For invalid IDs in routes, return 404 instead of 400
                        raise NotFoundError(f"Resource with ID {kwargs[param_name]} not found")
            
            # Now process query parameters
            for param, rule in validations.items():
                # Skip parameters that are already in kwargs (URL path parameters)
                if param in kwargs:
                    continue
                    
                value = request.args.get(param)
                
                # Handle tuple rules
                if isinstance(rule, tuple):
                    # Extract rule components with safe unpacking
                    param_type = rule[0] if len(rule) > 0 else str
                    required = rule[1] if len(rule) > 1 else False
                    
                    # Safely get default and custom validator
                    default = None
                    custom_validator = None
                    
                    if len(rule) > 2:
                        default = rule[2]
                    if len(rule) > 3:
                        custom_validator = rule[3]
                    
                    # Check if parameter is required
                    if required and value is None:
                        errors.append(f"{param} is required")
                        continue
                    
                    # Use default value if provided
                    if value is None and default is not None:
                        if callable(default) and not isinstance(default, type):
                            # If default is a function (not a type), call it to get the value
                            validated_params[param] = default()
                        else:
                            validated_params[param] = default
                        continue
                    
                    # Convert type if value exists
                    if value is not None:
                        try:
                            if param_type == datetime:
                                typed_value = datetime.strptime(value, '%Y-%m-%d')
                            elif param_type == bool:
                                typed_value = str(value).lower() in ('true', '1', 'yes')
                            else:
                                typed_value = param_type(value)
                                
                            # Apply custom validator if provided
                            if custom_validator and not custom_validator(typed_value):
                                errors.append(f"Invalid value for {param}")
                                continue
                                
                            validated_params[param] = typed_value
                        except (ValueError, TypeError):
                            errors.append(f"{param} must be of type {param_type.__name__}")
                
                # Handle function rules
                elif callable(rule):
                    if value is not None:
                        if not rule(value):
                            errors.append(f"Invalid value for {param}")
                        else:
                            validated_params[param] = value
            
            if errors:
                raise ValidationError(
                    message="Validation failed",
                    payload={"errors": errors}
                )
            
            # Add validated parameters to request object
            request.validated_params = validated_params
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(schema):
    """
    Decorator for validating JSON request bodies.
    
    Args:
        schema: Dictionary defining the expected JSON structure and validation rules.
    
    Example:
        @validate_json({
            'name': (str, True),
            'age': (int, False),
            'email': (str, True)
        })
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request must be JSON")
            
            data = request.get_json()
            errors = []
            validated_data = {}
            
            for field, (field_type, required) in schema.items():
                value = data.get(field)
                
                if required and value is None:
                    errors.append(f"{field} is required")
                    continue
                
                if value is not None:
                    try:
                        if field_type == datetime:
                            validated_data[field] = datetime.strptime(value, '%Y-%m-%d')
                        elif field_type == bool:
                            validated_data[field] = bool(value)
                        else:
                            validated_data[field] = field_type(value)
                    except (ValueError, TypeError):
                        errors.append(f"{field} must be of type {field_type.__name__}")
            
            if errors:
                raise ValidationError(
                    message="Validation failed",
                    payload={"errors": errors}
                )
            
            # Add validated data to request object
            request.validated_data = validated_data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_form(form_class):
    """
    Decorator for validating WTForms.
    
    Args:
        form_class: The WTForm class to use for validation
    
    Example:
        @validate_form(LoginForm)
        def login():
            form = request.validated_form
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            form = form_class()
            if request.method == 'POST':
                if not form.validate_on_submit():
                    errors = []
                    for field_name, field_errors in form.errors.items():
                        for error in field_errors:
                            errors.append(f"{field_name}: {error}")
                    raise ValidationError(
                        message="Form validation failed",
                        payload={"errors": errors}
                    )
            # Add validated form to request object
            request.validated_form = form
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email):
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Validate phone number format."""
    if not phone:
        return False
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_date_range(start_date, end_date):
    """Validate that end_date is after start_date."""
    if start_date and end_date:
        return end_date >= start_date
    return True

def validate_price(price):
    """Validate price is positive and has at most 2 decimal places."""
    if not price:
        return False
    try:
        price = float(price)
        return price >= 0 and len(str(price).split('.')[-1]) <= 2
    except (ValueError, TypeError):
        return False

def validate_username(username):
    """Validate username format."""
    if not username:
        return False
    # Username should be 3-32 characters long and contain only letters, numbers, and underscores
    pattern = r'^[a-zA-Z0-9_]{3,32}$'
    return bool(re.match(pattern, username))

def validate_password(password):
    """Validate password strength."""
    if not password:
        return False
    # Password should be at least 8 characters long and contain:
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one number
    # - At least one special character
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True 