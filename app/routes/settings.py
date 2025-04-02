"""
Settings management routes for the Car Repair and Sales Tracking application.

This module provides routes for:
1. Viewing and editing application settings
2. Managing users
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.setting import Setting
from app.models.user import User
from app.utils.auth import requires_role
from app.utils.validators import validate_form, validate_params
from app.utils.errors import ValidationError
from datetime import datetime
import json
import logging

settings_bp = Blueprint('settings', __name__)

# Default settings definitions with types and descriptions
DEFAULT_SETTINGS = {
    # Thresholds & Rules tab
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
    
    # General Configuration tab
    'enable_dark_mode': {
        'value': False,
        'type': 'bool',
        'description': 'Switch to a dark theme for the interface'
    }
}

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@requires_role('admin')
def index():
    """Settings index page with tabs"""
    
    # Handle POST request (form submissions)
    if request.method == 'POST':
        form_action = request.form.get('form_action', '')
        
        # Handle different form submissions based on the form_action field
        if form_action == 'update_thresholds':
            return handle_thresholds_update()
        elif form_action == 'update_general':
            return handle_general_update()
        else:
            flash('Invalid form submission', 'danger')
            return redirect(url_for('settings.index'))
    
    # Handle GET request (page load)
    try:
        # Get users for user management tab
        users = User.query.order_by(User.username).all()
        
        # Initialize settings dictionaries
        thresholds_settings = {}
        general_settings = {}
        
        # Load settings with defaults for missing values
        for key, config in DEFAULT_SETTINGS.items():
            value = Setting.get_setting(key, config['value'])
            
            setting_data = {
                'key': key,
                'value': value,
                'description': config['description'],
                'type': config['type']
            }
            
            # Organize settings by tab
            if key in ['stand_aging_threshold_days', 'status_inactivity_threshold_days', 
                      'enable_depreciation_tracking', 'enable_status_warnings', 'enable_subform_dropdowns']:
                thresholds_settings[key] = setting_data
            elif key in ['enable_dark_mode']:
                general_settings[key] = setting_data
        
        # Render template with all settings data
        return render_template('settings/index.html',
                               thresholds_settings=thresholds_settings,
                               general_settings=general_settings,
                               users=users,
                               active_tab=request.args.get('tab', 'general'))
    
    except Exception as e:
        logging.error(f"Error loading settings page: {str(e)}")
        flash(f"Error loading settings: {str(e)}", 'danger')
        return redirect(url_for('main.dashboard'))


def handle_thresholds_update():
    """Handle Thresholds & Rules tab form submission"""
    try:
        # Extract and validate numeric fields
        errors = []
        
        # Validate integer fields
        int_fields = {
            'stand_aging_threshold_days': 'Stand Aging Threshold',
            'status_inactivity_threshold_days': 'Status Inactivity Threshold'
        }
        
        for field_key, field_label in int_fields.items():
            value = request.form.get(field_key, '')
            if not value:
                errors.append(f"{field_label} is required")
            else:
                try:
                    int_value = int(value)
                    if int_value < 1:
                        errors.append(f"{field_label} must be at least 1")
                    else:
                        # Save valid value
                        Setting.set_setting(
                            field_key, 
                            int_value, 
                            description=DEFAULT_SETTINGS[field_key]['description'],
                            type='int'
                        )
                except ValueError:
                    errors.append(f"{field_label} must be a valid integer")
        
        # Process boolean toggles
        bool_fields = [
            'enable_depreciation_tracking',
            'enable_status_warnings',
            'enable_subform_dropdowns'
        ]
        
        for field_key in bool_fields:
            # Form returns 'on' for checked checkboxes, None for unchecked
            value = request.form.get(field_key) == 'on'
            Setting.set_setting(
                field_key, 
                value,
                description=DEFAULT_SETTINGS[field_key]['description'],
                type='bool'
            )
        
        # Handle errors or success
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            flash('Threshold settings updated successfully', 'success')
            
    except Exception as e:
        logging.error(f"Error updating threshold settings: {str(e)}")
        flash(f'Error updating settings: {str(e)}', 'danger')
        
    return redirect(url_for('settings.index', tab='thresholds'))


def handle_general_update():
    """Handle General Configuration tab form submission"""
    try:
        # Process boolean toggles
        bool_fields = ['enable_dark_mode']
        
        for field_key in bool_fields:
            # Form returns 'on' for checked checkboxes, None for unchecked
            value = request.form.get(field_key) == 'on'
            Setting.set_setting(
                field_key, 
                value,
                description=DEFAULT_SETTINGS[field_key]['description'],
                type='bool'
            )
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'General settings updated successfully'})
        
        flash('General settings updated successfully', 'success')
            
    except Exception as e:
        logging.error(f"Error updating general settings: {str(e)}")
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': f'Error updating settings: {str(e)}'}), 500
            
        flash(f'Error updating settings: {str(e)}', 'danger')
        
    return redirect(url_for('settings.index', tab='general'))


@settings_bp.route('/users/create', methods=['POST'])
@login_required
@requires_role('admin')
def create_user():
    """Create a new user"""
    try:
        # Extract form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', '').strip()
        
        # Validate required fields
        if not username or not password or not full_name or not role:
            raise ValueError("All fields are required")
            
        # Validate username is unique
        if User.query.filter_by(username=username).first():
            raise ValueError(f"Username '{username}' is already in use")
            
        # Validate passwords match
        if password != confirm_password:
            raise ValueError("Passwords do not match")
            
        # Validate role
        if role not in ['admin', 'manager', 'user']:
            raise ValueError("Invalid role")
            
        # Create new user
        user = User(
            username=username,
            full_name=full_name,
            role=role
        )
        user.password = password  # This will hash the password
        
        db.session.add(user)
        db.session.commit()
        
        flash(f"User '{username}' created successfully", 'success')
        
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        flash(f"Error creating user: {str(e)}", 'danger')
        
    return redirect(url_for('settings.index', tab='users'))


@settings_bp.route('/users/edit/<int:user_id>', methods=['POST'])
@login_required
@requires_role('admin')
def edit_user(user_id):
    """Edit an existing user"""
    try:
        # Check if user exists
        user = User.query.get_or_404(user_id)
        
        # Extract form data
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', '').strip()
        
        # Optional password change
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate required fields
        if not full_name or not role:
            raise ValueError("Name and role are required")
            
        # Validate role
        if role not in ['admin', 'manager', 'user']:
            raise ValueError("Invalid role")
            
        # Update user
        user.full_name = full_name
        user.role = role
        
        # Update password if provided
        if password:
            if password != confirm_password:
                raise ValueError("Passwords do not match")
            user.password = password  # This will hash the password
            
        db.session.commit()
        flash(f"User '{user.username}' updated successfully", 'success')
        
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logging.error(f"Error updating user: {str(e)}")
        flash(f"Error updating user: {str(e)}", 'danger')
        
    return redirect(url_for('settings.index', tab='users'))


@settings_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@requires_role('admin')
def delete_user(user_id):
    """Delete a user"""
    try:
        # Check if user exists
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting current user
        if user.user_id == current_user.user_id:
            raise ValueError("You cannot delete your own account")
            
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        flash(f"User '{user.username}' deleted successfully", 'success')
        
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logging.error(f"Error deleting user: {str(e)}")
        flash(f"Error deleting user: {str(e)}", 'danger')
        
    return redirect(url_for('settings.index', tab='users')) 