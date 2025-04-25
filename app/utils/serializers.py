"""
Serialization utilities for the Car Repair and Sales Tracking application.

This module provides functions for serializing various data types for JSON responses.
"""

import decimal
import json
from datetime import datetime, date

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal JSON serialization"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def decimal_to_float(obj):
    """
    Convert decimal.Decimal objects to float for JSON serialization
    
    Args:
        obj: The object or data structure to convert
        
    Returns:
        A new object with all decimal.Decimal values converted to float
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(decimal_to_float(i) for i in obj)
    return obj 