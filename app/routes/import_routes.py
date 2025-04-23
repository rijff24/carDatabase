"""
Import routes for the Car Repair and Sales Tracking application.

This module provides routes for bulk importing:
1. Cars
2. Repairs
3. Sales
4. Dealers
5. Parts
6. Stands
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from app.utils.auth import requires_role
from werkzeug.utils import secure_filename
import os
import logging
import io

# Import helper functions (these will be implemented separately)
from app.utils.import_helpers import (
    import_cars,
    import_repairs,
    import_sales,
    import_dealers,
    import_parts,
    import_stands,
    create_sample_template
)

# Create blueprint
import_bp = Blueprint('import', __name__)

# File upload configuration
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@import_bp.route('/')
@login_required
@requires_role('admin')
def index():
    """Main import page with multiple import forms"""
    # Check if template download requested
    template_type = request.args.get('download_template')
    if template_type:
        return download_template(template_type)
        
    return render_template('import/import.html')

@import_bp.route('/download-template/<entity_type>')
@login_required
@requires_role('admin')
def download_template(entity_type):
    """Generate and download a sample template for the specified entity type"""
    valid_types = ['cars', 'repairs', 'sales', 'dealers', 'parts', 'stands']
    
    if entity_type not in valid_types:
        flash(f"Invalid template type: {entity_type}", "danger")
        return redirect(url_for('import.index'))
    
    try:
        # Get the sample template Excel file
        excel_file = create_sample_template(entity_type)
        
        # Generate filename
        filename = f"{entity_type}_import_template.xlsx"
        
        # Return the file
        return send_file(
            excel_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logging.error(f"Error generating template: {str(e)}")
        flash(f"Error generating template: {str(e)}", "danger")
        return redirect(url_for('import.index'))

@import_bp.route('/cars', methods=['POST'])
@login_required
@requires_role('admin')
def import_cars_route():
    """Handle car import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_cars(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} cars imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing cars: {str(e)}")
            flash(f'Error importing cars: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index'))

@import_bp.route('/repairs', methods=['POST'])
@login_required
@requires_role('admin')
def import_repairs_route():
    """Handle repairs import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_repairs(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} repairs imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing repairs: {str(e)}")
            flash(f'Error importing repairs: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index'))

@import_bp.route('/sales', methods=['POST'])
@login_required
@requires_role('admin')
def import_sales_route():
    """Handle sales import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_sales(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} sales imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing sales: {str(e)}")
            flash(f'Error importing sales: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index'))

@import_bp.route('/dealers', methods=['POST'])
@login_required
@requires_role('admin')
def import_dealers_route():
    """Handle dealers import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_dealers(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} dealers imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing dealers: {str(e)}")
            flash(f'Error importing dealers: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index'))

@import_bp.route('/parts', methods=['POST'])
@login_required
@requires_role('admin')
def import_parts_route():
    """Handle parts import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_parts(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} parts imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing parts: {str(e)}")
            flash(f'Error importing parts: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index'))

@import_bp.route('/stands', methods=['POST'])
@login_required
@requires_role('admin')
def import_stands_route():
    """Handle stands import"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import.index'))
    
    if file and allowed_file(file.filename):
        try:
            # Process the uploaded file
            filename = secure_filename(file.filename)
            result = import_stands(file)
            
            # Flash the results
            flash(f'Import completed: {result["success"]} stands imported successfully, {result["failed"]} failed', 
                  'success' if result["success"] > 0 else 'warning')
            
            if result["errors"]:
                for error in result["errors"][:5]:  # Show first 5 errors
                    flash(f'Error: {error}', 'danger')
                if len(result["errors"]) > 5:
                    flash(f'... and {len(result["errors"]) - 5} more errors', 'danger')
                    
        except Exception as e:
            logging.error(f"Error importing stands: {str(e)}")
            flash(f'Error importing stands: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'danger')
        
    return redirect(url_for('import.index')) 