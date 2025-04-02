from app import db
from datetime import datetime
from sqlalchemy.sql import func

class Setting(db.Model):
    """Model for storing application settings"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), default='str')  # str, int, bool
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Setting {self.key}>'
    
    @classmethod
    def get_setting(cls, key, default=None, as_type=None):
        """Get a setting value by key with optional default value
        
        Args:
            key (str): The setting key to retrieve
            default: The default value if setting does not exist
            as_type (type, optional): Force conversion to this type
            
        Returns:
            The setting value, converted to the appropriate type
        """
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default
        
        # Determine conversion type
        convert_type = as_type or setting.type
        
        # Convert value based on type
        try:
            if convert_type == 'int':
                return int(setting.value)
            elif convert_type == 'float':
                return float(setting.value)
            elif convert_type == 'bool':
                return setting.value.lower() in ('true', '1', 'yes', 'y', 'on')
            else:
                return setting.value
        except (ValueError, TypeError):
            # If conversion fails, return the default
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None, type=None):
        """Set a setting value, creating it if it doesn't exist
        
        Args:
            key (str): The setting key
            value: The value to set (will be converted to string)
            description (str, optional): Setting description
            type (str, optional): Data type (str, int, bool)
            
        Returns:
            Setting: The updated or new Setting object
        """
        # Convert value to string for storage
        value_str = str(value)
        
        # Infer type if not provided
        if type is None:
            if isinstance(value, bool):
                type = 'bool'
            elif isinstance(value, int):
                type = 'int' 
            elif isinstance(value, float):
                type = 'float'
            else:
                type = 'str'
        
        # Find existing setting or create new one
        setting = cls.query.filter_by(key=key).first()
        
        if setting:
            # Update existing setting
            setting.value = value_str
            if description is not None:
                setting.description = description
            if type is not None:
                setting.type = type
        else:
            # Create new setting
            setting = cls(
                key=key,
                value=value_str,
                description=description,
                type=type
            )
            db.session.add(setting)
            
        # Save changes
        db.session.commit()
        return setting
    
    @classmethod
    def get_all_settings(cls):
        """Get all settings as a dictionary
        
        Returns:
            dict: Dictionary of all settings {key: value}
        """
        settings = {}
        for setting in cls.query.all():
            # Convert to appropriate type
            if setting.type == 'int':
                settings[setting.key] = int(setting.value)
            elif setting.type == 'float':
                settings[setting.key] = float(setting.value)
            elif setting.type == 'bool':
                settings[setting.key] = setting.value.lower() in ('true', '1', 'yes', 'y', 'on')
            else:
                settings[setting.key] = setting.value
        return settings 