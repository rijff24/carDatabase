"""
Helpers for importing data from CSV and Excel files.

These functions handle the parsing and validation of imported data.
"""

import pandas as pd
import logging
from app import db
from werkzeug.datastructures import FileStorage
from typing import Dict, List, Any, Union
from datetime import datetime
from app.models.car import Car, VehicleMake, VehicleModel, VehicleColor
from app.models.dealer import Dealer
from app.models.stand import Stand
from sqlalchemy.exc import SQLAlchemyError
import re
import os
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from io import BytesIO


def import_cars(file: FileStorage) -> Dict[str, Any]:
    """
    Import cars from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Car import started")
    success_count = 0
    fail_count = 0
    errors = []
    
    try:
        # Validate file format and read into DataFrame
        if not file or not file.filename:
            errors.append("No file provided")
            return {"success": 0, "failed": 0, "errors": errors}
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1][1:].lower()
        if file_ext not in ['csv', 'xlsx']:
            errors.append(f"Unsupported file format: {file_ext}. Please use CSV or Excel (.xlsx)")
            return {"success": 0, "failed": 0, "errors": errors}
        
        # Read file into DataFrame
        try:
            if file_ext == 'csv':
                df = pd.read_csv(file.stream)
            else:  # xlsx
                df = pd.read_excel(file.stream)
        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")
            return {"success": 0, "failed": 0, "errors": errors}
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("File contains no data")
            return {"success": 0, "failed": 0, "errors": errors}
        
        # Validate required columns
        required_columns = ['VIN', 'Make', 'Model', 'Year', 'Colour', 'Purchase Price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return {"success": 0, "failed": 0, "errors": errors}
        
        # Process each row
        for index, row in df.iterrows():
            row_errors = []
            
            # Basic validation for required fields
            if pd.isna(row.get('VIN')) or not str(row.get('VIN')).strip():
                row_errors.append('VIN is required')
            
            if pd.isna(row.get('Make')) or not str(row.get('Make')).strip():
                row_errors.append('Make is required')
            
            if pd.isna(row.get('Model')) or not str(row.get('Model')).strip():
                row_errors.append('Model is required')
            
            if pd.isna(row.get('Year')):
                row_errors.append('Year is required')
            
            if pd.isna(row.get('Colour')) or not str(row.get('Colour')).strip():
                row_errors.append('Colour is required')
            
            if pd.isna(row.get('Purchase Price')):
                row_errors.append('Purchase Price is required')
            
            # Skip row if validation errors
            if row_errors:
                fail_count += 1
                errors.append(f"Row {index+2}: {'; '.join(row_errors)}")
                continue
            
            # Extract and sanitize values
            try:
                # Required fields
                vin = str(row.get('VIN')).strip().upper()
                make_str = str(row.get('Make')).strip()
                model_str = str(row.get('Model')).strip()
                year = int(row.get('Year'))
                colour = str(row.get('Colour')).strip()
                purchase_price = float(row.get('Purchase Price'))
                
                # Optional fields with defaults
                purchase_date = row.get('Purchase Date')
                if pd.isna(purchase_date):
                    purchase_date = datetime.now().date()
                elif isinstance(purchase_date, str):
                    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                elif isinstance(purchase_date, datetime):
                    purchase_date = purchase_date.date()
                
                refuel_cost = float(row.get('Refuel Cost', 0)) if not pd.isna(row.get('Refuel Cost')) else 0
                
                status = str(row.get('Status', 'Available')).strip() if not pd.isna(row.get('Status')) else 'Available'
                
                # Check for duplicate VIN
                existing_car = Car.query.filter_by(licence_number=vin).first()
                if existing_car:
                    fail_count += 1
                    errors.append(f"Row {index+2}: Car with VIN {vin} already exists")
                    continue
                
                # Handle relationships
                # 1. Make and Model
                make_obj = VehicleMake.get_or_create(make_str)
                if not make_obj:
                    fail_count += 1
                    errors.append(f"Row {index+2}: Failed to create/find make '{make_str}'")
                    continue
                
                model_obj = VehicleModel.get_or_create(model_str, make_obj.id)
                if not model_obj:
                    fail_count += 1
                    errors.append(f"Row {index+2}: Failed to create/find model '{model_str}'")
                    continue
                
                # 2. Colour
                colour_obj = None
                try:
                    colour_sanitized = VehicleColor.sanitize_name(colour)
                    # Check if color exists
                    colour_obj = VehicleColor.query.filter(
                        db.func.lower(VehicleColor.name) == db.func.lower(colour_sanitized)
                    ).first()
                    
                    # Create if not exists
                    if not colour_obj:
                        colour_obj = VehicleColor(name=colour_sanitized)
                        db.session.add(colour_obj)
                        db.session.flush()  # Get ID without committing
                except Exception as e:
                    logging.error(f"Error processing color: {str(e)}")
                
                # 3. Dealer
                dealer_id = None
                if 'Dealer' in row and not pd.isna(row.get('Dealer')):
                    dealer_name = str(row.get('Dealer')).strip()
                    dealer = Dealer.query.filter(
                        db.func.lower(Dealer.dealer_name) == db.func.lower(dealer_name)
                    ).first()
                    if dealer:
                        dealer_id = dealer.dealer_id
                
                # 4. Stand
                stand_id = None
                if 'Stand' in row and not pd.isna(row.get('Stand')):
                    stand_name = str(row.get('Stand')).strip()
                    stand = Stand.query.filter(
                        db.func.lower(Stand.stand_name) == db.func.lower(stand_name)
                    ).first()
                    if stand:
                        stand_id = stand.stand_id
                
                # Create the new car
                new_car = Car(
                    vehicle_name=f"{year} {make_obj.name} {model_obj.name}",
                    vehicle_make=make_obj.name,
                    vehicle_model=model_obj.name,
                    year=year,
                    colour=colour_sanitized,
                    dekra_condition="Good",  # Default 
                    licence_number=vin,
                    registration_number=vin,  # Default to VIN if not provided
                    purchase_price=purchase_price,
                    source="Import",
                    date_bought=purchase_date,
                    refuel_cost=refuel_cost,
                    current_location="Showroom",  # Default
                    repair_status=status,
                    stand_id=stand_id,
                    dealer_id=dealer_id
                )
                
                # Add to database
                db.session.add(new_car)
                db.session.commit()
                success_count += 1
                
            except Exception as e:
                db.session.rollback()
                fail_count += 1
                errors.append(f"Row {index+2}: Error processing data: {str(e)}")
                logging.error(f"Error processing row {index+2}: {str(e)}")
    except Exception as e:
        logging.error(f"Overall import error: {str(e)}")
        errors.append(f"Import process error: {str(e)}")
    
    return {
        "success": success_count,
        "failed": fail_count,
        "errors": errors
    }


def import_repairs(file: FileStorage) -> Dict[str, Any]:
    """
    Import repairs from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Repairs import started")
    # The implementation will be done later
    # For now, return a stub response
    return {
        "success": 0,
        "failed": 0,
        "errors": []
    }


def import_sales(file: FileStorage) -> Dict[str, Any]:
    """
    Import sales from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Sales import started")
    # The implementation will be done later
    # For now, return a stub response
    return {
        "success": 0,
        "failed": 0,
        "errors": []
    }


def import_dealers(file: FileStorage) -> Dict[str, Any]:
    """
    Import dealers from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Dealers import started")
    # The implementation will be done later
    # For now, return a stub response
    return {
        "success": 0,
        "failed": 0,
        "errors": []
    }


def import_parts(file: FileStorage) -> Dict[str, Any]:
    """
    Import parts from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Parts import started")
    # The implementation will be done later
    # For now, return a stub response
    return {
        "success": 0,
        "failed": 0,
        "errors": []
    }


def import_stands(file: FileStorage) -> Dict[str, Any]:
    """
    Import stands from a CSV or Excel file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        dict: Results of the import with success and failure counts
    """
    logging.info("Stands import started")
    # The implementation will be done later
    # For now, return a stub response
    return {
        "success": 0,
        "failed": 0,
        "errors": []
    }


def create_sample_template(entity_type: str) -> BytesIO:
    """
    Create a sample import template for the specified entity type.
    
    Args:
        entity_type: Type of entity (cars, repairs, sales, dealers, parts, stands)
        
    Returns:
        BytesIO: Excel file buffer with formatted template
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Import Template"
    
    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    required_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Define templates with column descriptions
    templates = {
        'cars': {
            'columns': [
                ('VIN', 'Vehicle Identification Number (17 characters)', True),
                ('Make', 'Vehicle manufacturer (e.g., Toyota, Honda)', True),
                ('Model', 'Vehicle model name', True),
                ('Year', 'Manufacturing year (1990-2024)', True),
                ('Color', 'Vehicle color', True),
                ('Purchase Date', 'Date of purchase (YYYY-MM-DD)', True),
                ('Purchase Price', 'Purchase price in Rands', True),
                ('Refuel Cost', 'Cost to refuel the vehicle', False),
                ('Dealer', 'Name of the dealer', True),
                ('Stand', 'Name of the stand', True),
                ('Status', 'Current status (Available, In Repair, Sold)', True)
            ],
            'sample_data': [
                ['1HGCM82633A123456', 'Honda', 'Accord', 2023, 'Black', '2023-01-15', 250000, 500, 'City Motors', 'Main Showroom', 'Available'],
                ['5TFUM5F10DX007890', 'Toyota', 'Tundra', 2022, 'Red', '2023-02-20', 350000, 600, 'Highway Auto', 'Downtown Location', 'In Repair']
            ]
        },
        'repairs': {
            'columns': [
                ('Car ID', 'ID of the car being repaired', True),
                ('Description', 'Description of the repair', True),
                ('Cost', 'Cost of the repair in Rands', True),
                ('Provider ID', 'ID of the repair provider', True),
                ('Repair Date', 'Date of repair (YYYY-MM-DD)', True)
            ],
            'sample_data': [
                [1, 'Oil Change', 1500.00, 1, '2023-01-15'],
                [2, 'Brake Replacement', 3500.00, 2, '2023-02-20']
            ]
        },
        'sales': {
            'columns': [
                ('Car ID', 'ID of the car being sold', True),
                ('Customer Name', 'Name of the customer', True),
                ('Sale Price', 'Sale price in Rands', True),
                ('Sale Date', 'Date of sale (YYYY-MM-DD)', True),
                ('Payment Method', 'Method of payment', True)
            ],
            'sample_data': [
                [1, 'John Doe', 280000, '2023-03-10', 'Bank Transfer'],
                [2, 'Jane Smith', 380000, '2023-04-15', 'Cash']
            ]
        },
        'dealers': {
            'columns': [
                ('Name', 'Name of the dealer', True),
                ('Address', 'Physical address', True),
                ('Contact Name', 'Name of the contact person', True),
                ('Phone', 'Contact phone number', True),
                ('Email', 'Contact email address', True)
            ],
            'sample_data': [
                ['City Motors', '123 Main St', 'Mike Johnson', '555-123-4567', 'mike@cityauto.com'],
                ['Highway Auto', '456 Route 7', 'Sarah Williams', '555-987-6543', 'sarah@highway.com']
            ]
        },
        'parts': {
            'columns': [
                ('Part Name', 'Name of the part', True),
                ('Manufacturer', 'Part manufacturer', True),
                ('Standard Price', 'Standard price in Rands', True),
                ('Stock Quantity', 'Current stock quantity', True)
            ],
            'sample_data': [
                ['Oil Filter', 'Bosch', 299.99, 50],
                ['Brake Pads', 'ACDelco', 899.99, 25]
            ]
        },
        'stands': {
            'columns': [
                ('Name', 'Name of the stand', True),
                ('Address', 'Physical address', True),
                ('Capacity', 'Maximum number of cars', True),
                ('Contact Person', 'Name of the contact person', True)
            ],
            'sample_data': [
                ['Main Showroom', '789 Industrial Pkwy', 50, 'Tom Brown'],
                ['Downtown Location', '101 Center St', 30, 'Lisa Green']
            ]
        }
    }
    
    if entity_type not in templates:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    template = templates[entity_type]
    
    # Write headers
    for col, (header, description, required) in enumerate(template['columns'], 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add description as comment
        cell.comment = Comment(description, "System")
        
        # Add yellow background for required fields
        if required:
            for row in range(2, len(template['sample_data']) + 2):
                ws.cell(row=row, column=col).fill = required_fill
    
    # Write sample data
    for row_idx, row_data in enumerate(template['sample_data'], 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Add data validation for specific columns
    if entity_type == 'cars':
        # Year validation (1990-2024)
        year_validation = DataValidation(
            type="whole",
            operator="between",
            formula1="1990",
            formula2="2024",
            allow_blank=True
        )
        year_validation.add(f"D2:D1000")
        ws.add_data_validation(year_validation)
        
        # Status validation
        status_validation = DataValidation(
            type="list",
            formula1='"Available,In Repair,Sold"',
            allow_blank=True
        )
        status_validation.add(f"K2:K1000")
        ws.add_data_validation(status_validation)
    
    # Adjust column widths
    for col in range(1, len(template['columns']) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 20
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output 