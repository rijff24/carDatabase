from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, make_response
from flask_login import login_required
from app import db
from app.reports import get_report
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Reports index page."""
    now = datetime.now()
    return render_template('reports/index.html', current_date=now.strftime('%Y-%m-%d'))

@reports_bp.route('/sales-performance')
@login_required
def sales_performance():
    """Sales Performance Report."""
    # Get parameters from request
    period = request.args.get('period', 'monthly')
    year = request.args.get('year', datetime.now().year)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_ids = request.args.getlist('stand_ids')
    
    # Handle empty period parameter
    if not period or period.strip() == '':
        period = 'monthly'
    
    # Convert year to integer if it's a string
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
    # Create report instance
    report_class = get_report('sales_performance')
    report = report_class(
        period=period, 
        year=year,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_ids=stand_ids
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'period': period,
            'year': year,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'stand_ids': stand_ids,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/sales-performance.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

# New route for development testing without login
@reports_bp.route('/test/sales-performance')
def test_sales_performance():
    """Development-only route for testing the Sales Performance Report without login."""
    # Get parameters from request
    period = request.args.get('period', 'monthly')
    year = request.args.get('year', datetime.now().year)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_ids = request.args.getlist('stand_ids')
    
    # Handle empty period parameter
    if not period or period.strip() == '':
        period = 'monthly'
    
    # Convert year to integer if it's a string
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
    # Create report instance
    report_class = get_report('sales_performance')
    report = report_class(
        period=period, 
        year=year,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_ids=stand_ids
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'period': period,
            'year': year,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'stand_ids': stand_ids,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/sales-performance.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "period": period,
                "year": year,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "stand_ids": stand_ids
            }
        }), 500

@reports_bp.route('/repair-analysis')
@login_required
def repair_analysis():
    """Repair Cost Analysis Report."""
    # Get parameters from request
    year = request.args.get('year', datetime.now().year)
    
    # Convert year to integer if it's a string
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Create report instance
    report_class = get_report('repair_analysis')
    report = report_class(year=year)
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'year': year,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data
        }
        
        # Render template with complete context
        return render_template('reports/repair-analysis.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/inventory-aging')
@login_required
def inventory_aging():
    """Inventory Aging Report."""
    # Get parameters from request
    status = request.args.get('status', 'all')
    stand_id = request.args.get('stand_id')
    make = request.args.get('make')
    model = request.args.get('model')
    min_age = request.args.get('min_age')
    max_age = request.args.get('max_age')
    
    # Convert numeric parameters to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
    
    if min_age and min_age.isdigit():
        min_age = int(min_age)
    else:
        min_age = 0
        
    if max_age and max_age.isdigit():
        max_age = int(max_age)
    else:
        max_age = None
    
    # Create report instance with all parameters
    report_class = get_report('inventory_aging')
    report = report_class(
        status=status,
        stand_id=stand_id,
        make=make,
        model=model,
        min_age=min_age,
        max_age=max_age
    )
    
    try:
        # Generate fresh report data
        data = report.generate()
        
        # Set cache control headers to prevent caching
        response = make_response(render_template('reports/inventory-aging.html', **data))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/profit-margin')
@login_required
def profit_margin():
    """Profit Margin Analysis Report."""
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    
    # Create report instance
    report_class = get_report('profit_margin')
    report = report_class(timeframe=timeframe)
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'timeframe': timeframe,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data
        }
        
        # Render template with complete context
        return render_template('reports/profit-margin.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

# API endpoints for testing (no login required)
@reports_bp.route('/api/sales-performance')
def api_sales_performance():
    """Sales Performance Report API endpoint."""
    # Get query parameters
    period = request.args.get('period', 'monthly')
    year = request.args.get('year', datetime.now().year)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_ids = request.args.getlist('stand_ids')
    
    # Handle empty period parameter
    if not period or period.strip() == '':
        period = 'monthly'
    
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
    # Create report
    report_class = get_report('sales_performance')
    report = report_class(
        period=period, 
        year=year,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_ids=stand_ids
    )
    data = report.generate()
    
    return jsonify(data)

@reports_bp.route('/api/repair-analysis')
def api_repair_analysis():
    """Repair Analysis Report API endpoint."""
    # Get query parameters
    year = request.args.get('year', datetime.now().year)
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    
    # Create report
    report_class = get_report('repair_analysis')
    report = report_class(year=year)
    data = report.generate()
    
    return jsonify(data)

@reports_bp.route('/api/inventory-aging')
def api_inventory_aging():
    """Inventory Aging Report API endpoint."""
    # Get query parameters
    status = request.args.get('status', 'all')
    stand_id = request.args.get('stand_id')
    make = request.args.get('make')
    model = request.args.get('model')
    min_age = request.args.get('min_age')
    max_age = request.args.get('max_age')
    
    # Convert numeric parameters to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
    
    if min_age and min_age.isdigit():
        min_age = int(min_age)
    else:
        min_age = 0
        
    if max_age and max_age.isdigit():
        max_age = int(max_age)
    else:
        max_age = None
    
    try:
        # Create report with all parameters
        report_class = get_report('inventory_aging')
        report = report_class(
            status=status,
            stand_id=stand_id,
            make=make,
            model=model,
            min_age=min_age,
            max_age=max_age
        )
        
        # Generate fresh report data
        data = report.generate()
        
        # Set cache control headers to prevent caching
        response = jsonify(data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error",
            "message": "An error occurred while generating the inventory aging report."
        }), 500

@reports_bp.route('/api/profit-margin')
def api_profit_margin():
    """Profit Margin Report API endpoint."""
    # Get query parameters
    timeframe = request.args.get('timeframe', 'last_30_days')
    
    # Create report
    report_class = get_report('profit_margin')
    report = report_class(timeframe=timeframe)
    data = report.generate()
    
    return jsonify(data)

@reports_bp.route('/debug/sales-performance')
def debug_sales_performance():
    """Debug endpoint for Sales Performance Report."""
    # Get parameters from request
    period = request.args.get('period', 'monthly')
    year = request.args.get('year', datetime.now().year)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_ids = request.args.getlist('stand_ids')
    
    # Handle empty period parameter
    if not period or period.strip() == '':
        period = 'monthly'
    
    # Convert year to integer if it's a string
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = None
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
    # Create report instance
    report_class = get_report('sales_performance')
    report = report_class(
        period=period, 
        year=year,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_ids=stand_ids
    )
    
    # Generate report data without rendering template
    try:
        data = report.generate()
        # Add request parameters for debugging
        data["debug"] = {
            "request_period": request.args.get('period', '(not provided)'),
            "resolved_period": period,
            "request_year": request.args.get('year', '(not provided)'),
            "resolved_year": year,
            "request_start_date": request.args.get('start_date', '(not provided)'),
            "resolved_start_date": str(start_date) if start_date else None,
            "request_end_date": request.args.get('end_date', '(not provided)'),
            "resolved_end_date": str(end_date) if end_date else None,
            "request_vehicle_make": request.args.get('vehicle_make', '(not provided)'),
            "resolved_vehicle_make": vehicle_make,
            "request_vehicle_model": request.args.get('vehicle_model', '(not provided)'),
            "resolved_vehicle_model": vehicle_model,
            "request_stand_ids": request.args.getlist('stand_ids'),
            "resolved_stand_ids": stand_ids
        }
        return jsonify(data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "period": period,
                "year": year,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "stand_ids": stand_ids
            }
        }), 500

# Test routes for development (no login required)
@reports_bp.route('/test/repair-analysis')
def test_repair_analysis():
    """Development-only route for testing the Repair Analysis Report without login."""
    # Get parameters from request
    year = request.args.get('year', datetime.now().year)
    
    # Convert year to integer if it's a string
    if isinstance(year, str) and year.isdigit():
        year = int(year)
    else:
        year = datetime.now().year
    
    # Create report instance
    report_class = get_report('repair_analysis')
    report = report_class(year=year)
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'year': year,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data
        }
        
        # Render template with complete context
        return render_template('reports/repair-analysis.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "year": year
            }
        }), 500

@reports_bp.route('/test/inventory-aging')
def test_inventory_aging():
    """Development-only route for testing the Inventory Aging Report without login."""
    # Get parameters from request
    status = request.args.get('status', 'all')
    stand_id = request.args.get('stand_id')
    make = request.args.get('make')
    model = request.args.get('model')
    min_age = request.args.get('min_age')
    max_age = request.args.get('max_age')
    
    # Convert numeric parameters to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
    
    if min_age and min_age.isdigit():
        min_age = int(min_age)
    else:
        min_age = 0
        
    if max_age and max_age.isdigit():
        max_age = int(max_age)
    else:
        max_age = None
    
    # Create report instance with all parameters
    report_class = get_report('inventory_aging')
    report = report_class(
        status=status,
        stand_id=stand_id,
        make=make,
        model=model,
        min_age=min_age,
        max_age=max_age
    )
    
    try:
        # Generate fresh report data
        data = report.generate()
        
        # Set cache control headers to prevent caching
        response = make_response(render_template('reports/inventory-aging.html', **data))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "status": status,
                "stand_id": stand_id,
                "make": make,
                "model": model,
                "min_age": min_age,
                "max_age": max_age
            }
        }), 500

@reports_bp.route('/test/profit-margin')
def test_profit_margin():
    """Development-only route for testing the Profit Margin Report without login."""
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    
    # Create report instance
    report_class = get_report('profit_margin')
    report = report_class(timeframe=timeframe)
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'timeframe': timeframe,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            **data
        }
        
        # Render template with complete context
        return render_template('reports/profit-margin.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "timeframe": timeframe
            }
        }), 500