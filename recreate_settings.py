"""
Script to recreate the settings table with the updated schema
"""

from app import create_app, db
from app.models.setting import Setting
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Drop and recreate the settings table
    try:
        # First, back up existing settings if any
        existing_settings = []
        try:
            settings = db.session.query(Setting).all()
            for setting in settings:
                existing_settings.append({
                    'key': setting.key,
                    'value': setting.value,
                    'description': getattr(setting, 'description', None),
                    'type': getattr(setting, 'type', 'str')
                })
            print(f"Backed up {len(existing_settings)} existing settings")
        except Exception as e:
            print(f"Error backing up settings: {str(e)}")
        
        # Drop the table
        db.session.execute(text('DROP TABLE IF EXISTS settings'))
        db.session.commit()
        print("Dropped settings table")
        
        # Create the table
        Setting.__table__.create(db.engine)
        print("Created settings table with new schema")
        
        # Restore settings
        for setting_data in existing_settings:
            setting = Setting(
                key=setting_data['key'],
                value=setting_data['value'],
                description=setting_data['description'],
                type=setting_data['type']
            )
            db.session.add(setting)
        
        # Add default settings if needed
        default_settings = {
            'stand_aging_threshold_days': {
                'value': 180,
                'type': 'int',
                'description': 'Number of days after which a car on a stand is considered aging'
            },
            'status_inactivity_threshold_days': {
                'value': 30,
                'type': 'int',
                'description': 'Number of days after which a car with unchanged status is considered inactive'
            },
            'enable_depreciation_tracking': {
                'value': False,
                'type': 'bool',
                'description': 'Track depreciation of vehicles over time'
            },
            'enable_status_warnings': {
                'value': True,
                'type': 'bool',
                'description': 'Show warnings for vehicles with stale status'
            },
            'enable_subform_dropdowns': {
                'value': True,
                'type': 'bool',
                'description': 'Use dropdown modals for subforms'
            },
            'enable_dark_mode': {
                'value': False,
                'type': 'bool',
                'description': 'Switch to a dark theme for the interface'
            }
        }
        
        # Add default settings that don't already exist
        for key, data in default_settings.items():
            if not db.session.query(Setting).filter(Setting.key == key).first():
                setting = Setting(
                    key=key,
                    value=str(data['value']),
                    description=data['description'],
                    type=data['type']
                )
                db.session.add(setting)
                print(f"Added default setting: {key}")
        
        db.session.commit()
        print("Settings restored and defaults added")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error recreating settings table: {str(e)}") 