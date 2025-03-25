from flask import request, render_template
from datetime import datetime
from app.utils.validators import validate_params
from abc import ABC, abstractmethod

class Report(ABC):
    """
    Base class for all reports
    """
    
    # Template path for this report
    template_path = None
    
    # Default parameters for the report
    default_params = {}
    
    # Parameter validation rules
    param_rules = {}
    
    def __init__(self):
        """
        Initialize a new report instance
        """
        self.params = {}
        self.data = {}
        self.report_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def validate_parameters(self):
        """
        Validate parameters for this report
        """
        # Use the validate_params decorator pattern but directly
        validated_params = {}
        
        # If no param rules defined, return empty dict
        if not self.param_rules:
            return {}
        
        for param_name, param_rule in self.param_rules.items():
            param_type, required, default_value, validator = None, False, None, None
            
            if isinstance(param_rule, tuple):
                if len(param_rule) >= 1:
                    param_type = param_rule[0]
                if len(param_rule) >= 2:
                    required = param_rule[1]
                if len(param_rule) >= 3:
                    default_value = param_rule[2]
                if len(param_rule) >= 4:
                    validator = param_rule[3]
            
            # Get parameter value from request
            value = request.args.get(param_name)
            
            # If not provided and a default is available, use it
            if value is None:
                if callable(default_value):
                    value = default_value()
                else:
                    value = default_value
            
            # Type conversion if needed
            if param_type and value is not None:
                try:
                    value = param_type(value)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid value for parameter '{param_name}'")
            
            # Validation if needed
            if validator and value is not None:
                if not validator(value):
                    raise ValueError(f"Invalid value for parameter '{param_name}'")
            
            # Add to validated parameters
            validated_params[param_name] = value
        
        self.params = validated_params
        return validated_params
    
    @abstractmethod
    def generate(self):
        """
        Generate the report data
        
        This method must be implemented by all subclasses.
        It should populate the self.data dictionary with the report data.
        """
        pass
    
    def render(self):
        """
        Render the report template with data
        """
        if not self.template_path:
            raise ValueError("template_path must be defined")
        
        # Combine params and data dictionaries
        context = {**self.params, **self.data, 'report_date': self.report_date}
        
        return render_template(self.template_path, **context)
    
    def get(self):
        """
        Process and render the report
        """
        try:
            # Validate parameters
            self.validate_parameters()
            
            # Generate report data
            self.generate()
            
            # Render the report
            return self.render()
            
        except ValueError as e:
            # Handle validation errors
            from flask import flash, redirect, url_for
            flash(str(e), 'danger')
            return redirect(url_for('reports.index')) 