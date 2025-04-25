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

@reports_bp.route('/stand-performance')
@login_required
def stand_performance():
    """Stand Performance Report."""
    # Get parameters from request
    stand_ids = request.args.getlist('stand_ids')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
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
    
    # Create report instance
    report_class = get_report('stand_performance')
    report = report_class(
        stand_ids=stand_ids,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'stand_ids': stand_ids,
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/stand-performance.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/api/stand-performance')
def api_stand_performance():
    """API endpoint for Stand Performance Report data export."""
    # Get parameters from request
    stand_ids = request.args.getlist('stand_ids')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    format = request.args.get('format', 'xlsx')
    detail = request.args.get('detail', 'full')
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
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
    
    # Create report instance
    report_class = get_report('stand_performance')
    report = report_class(
        stand_ids=stand_ids,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Prepare response based on format
        if format == 'json':
            # Return JSON data
            return jsonify(data)
        elif format == 'csv':
            # Generate CSV from data
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = ['Stand Name', 'Location', 'Current Cars', 'Current Utilization', 
                      'Avg Age (Current)', 'Cars Sold', 'Avg Days on Stand', 
                      'Total Profit', 'Turnover Rate']
            writer.writerow(headers)
            
            # Write stand data rows
            for stand in data['stands']:
                row = [
                    stand['stand_name'],
                    stand['location'],
                    stand['current_cars'],
                    f"{round(stand['utilization'], 1)}%",
                    round(stand['current_avg_age'], 1),
                    stand['sold_cars'],
                    round(stand['avg_days_on_stand'], 1),
                    round(float(stand['total_profit']), 2),
                    f"{round(stand['turnover_rate'] * 100, 1)}%"
                ]
                writer.writerow(row)
            
            # Create response
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=stand_performance_report.csv"
            response.headers["Content-type"] = "text/csv"
            return response
        else:  # Default to xlsx
            # Generate Excel from data
            import xlsxwriter
            import io
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            
            # Create formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FFC107',
                'border': 1
            })
            cell_format = workbook.add_format({
                'border': 1
            })
            number_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0.00'
            })
            percent_format = workbook.add_format({
                'border': 1,
                'num_format': '0.0%'
            })
            
            # Add summary worksheet
            summary_sheet = workbook.add_worksheet('Summary')
            
            # Add summary data
            summary_sheet.write(0, 0, 'Stand Performance Report Summary', header_format)
            summary_sheet.write(1, 0, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", cell_format)
            
            summary_sheet.write(3, 0, 'Total Stands', header_format)
            summary_sheet.write(3, 1, data['summary']['total_stands'], cell_format)
            
            summary_sheet.write(4, 0, 'Total Cars on Stand', header_format)
            summary_sheet.write(4, 1, data['summary']['total_cars_on_stand'], cell_format)
            
            summary_sheet.write(5, 0, 'Total Cars Sold', header_format)
            summary_sheet.write(5, 1, data['summary']['total_cars_sold'], cell_format)
            
            summary_sheet.write(6, 0, 'Overall Avg Days on Stand', header_format)
            summary_sheet.write(6, 1, data['summary']['overall_avg_days_on_stand'], number_format)
            
            summary_sheet.write(7, 0, 'Total Profit', header_format)
            summary_sheet.write(7, 1, float(data['summary']['total_profit']), number_format)
            
            summary_sheet.write(8, 0, 'Overall Turnover Rate', header_format)
            summary_sheet.write(8, 1, data['summary']['overall_turnover_rate'], percent_format)
            
            # Set column widths
            summary_sheet.set_column(0, 0, 25)
            summary_sheet.set_column(1, 1, 15)
            
            # Add details worksheet
            details_sheet = workbook.add_worksheet('Stand Details')
            
            # Add headers
            headers = ['Stand Name', 'Location', 'Current Cars', 'Current Utilization', 
                      'Avg Age (Current)', 'Cars Sold', 'Avg Days on Stand', 
                      'Total Profit', 'Turnover Rate']
            
            for col, header in enumerate(headers):
                details_sheet.write(0, col, header, header_format)
            
            # Add data rows
            for row, stand in enumerate(data['stands'], start=1):
                details_sheet.write(row, 0, stand['stand_name'], cell_format)
                details_sheet.write(row, 1, stand['location'], cell_format)
                details_sheet.write(row, 2, stand['current_cars'], cell_format)
                details_sheet.write(row, 3, stand['utilization'] / 100, percent_format)
                details_sheet.write(row, 4, stand['current_avg_age'], number_format)
                details_sheet.write(row, 5, stand['sold_cars'], cell_format)
                details_sheet.write(row, 6, stand['avg_days_on_stand'], number_format)
                details_sheet.write(row, 7, float(stand['total_profit']), number_format)
                details_sheet.write(row, 8, stand['turnover_rate'], percent_format)
            
            # Add aging analysis worksheet
            aging_sheet = workbook.add_worksheet('Aging Analysis')
            
            # Add headers
            aging_headers = ['Stand Name', 'Fresh (0-30 days)', 'Normal (31-60 days)', 
                           f"Aging (61-{data['stand_aging_threshold_days']} days)", 
                           f"Critical (>{data['stand_aging_threshold_days']} days)", 'Total']
            
            for col, header in enumerate(aging_headers):
                aging_sheet.write(0, col, header, header_format)
            
            # Add data rows
            for row, stand in enumerate(data['stands'], start=1):
                aging_sheet.write(row, 0, stand['stand_name'], cell_format)
                aging_sheet.write(row, 1, stand['aging_bands']['fresh'], cell_format)
                aging_sheet.write(row, 2, stand['aging_bands']['normal'], cell_format)
                aging_sheet.write(row, 3, stand['aging_bands']['aging'], cell_format)
                aging_sheet.write(row, 4, stand['aging_bands']['critical'], cell_format)
                aging_sheet.write(row, 5, stand['current_cars'], cell_format)
            
            # Set column widths
            details_sheet.set_column(0, 0, 20)
            details_sheet.set_column(1, 1, 20)
            details_sheet.set_column(2, 8, 15)
            
            aging_sheet.set_column(0, 0, 20)
            aging_sheet.set_column(1, 5, 15)
            
            # Close workbook
            workbook.close()
            
            # Create response
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=stand_performance_report.xlsx"
            response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return response
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "stand_ids": stand_ids,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "format": format,
                "detail": detail
            }
        }), 500

@reports_bp.route('/test/stand-performance')
def test_stand_performance():
    """Development-only route for testing the Stand Performance Report without login."""
    # Get parameters from request
    stand_ids = request.args.getlist('stand_ids')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    
    # Convert stand_ids to integers
    if stand_ids:
        stand_ids = [int(stand_id) for stand_id in stand_ids if stand_id.isdigit()]
    
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
    
    # Create report instance
    report_class = get_report('stand_performance')
    report = report_class(
        stand_ids=stand_ids,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'stand_ids': stand_ids,
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/stand-performance.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "stand_ids": stand_ids,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model
            }
        }), 500

@reports_bp.route('/repair-history')
@login_required
def repair_history():
    """Repair Cost & History Report."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    provider_id = request.args.get('provider_id')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    year = request.args.get('year')
    
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
    
    # Convert provider_id to integer if it's a string
    if provider_id and provider_id.isdigit():
        provider_id = int(provider_id)
    else:
        provider_id = None
    
    # Convert year to integer if it's a string
    if year and year.isdigit():
        year = int(year)
    else:
        year = None
    
    # Create report instance
    report_class = get_report('repair_history')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        repair_type=repair_type,
        provider_id=provider_id,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        year=year
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Check if there are any filters applied
        has_filters_applied = any([
            start_date, end_date, repair_type, 
            provider_id, vehicle_make, vehicle_model, year
        ])
        
        # Ensure all necessary parameters are included
        context = {
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
            'repair_type': repair_type,
            'provider_id': provider_id,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'year': year,
            'has_filters_applied': has_filters_applied,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/repair-history.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/repair-history/export')
@login_required
def repair_history_export():
    """Export Repair Cost & History Report to various formats."""
    # Get export format from request
    export_format = request.args.get('format', 'xlsx')
    
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    provider_id = request.args.get('provider_id')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    year = request.args.get('year')
    
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
    
    # Convert provider_id to integer if it's a string
    if provider_id and provider_id.isdigit():
        provider_id = int(provider_id)
    else:
        provider_id = None
    
    # Convert year to integer if it's a string
    if year and year.isdigit():
        year = int(year)
    else:
        year = None
    
    # Create report instance
    report_class = get_report('repair_history')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        repair_type=repair_type,
        provider_id=provider_id,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        year=year
    )
    
    try:
        # Export based on format
        if export_format == 'xlsx':
            # Export to Excel
            excel_data = report.export_xlsx()
            
            # Prepare filename
            filename = f"repair_history_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Create response
            response = make_response(excel_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        else:
            flash(f"Unsupported export format: {export_format}", "danger")
            return redirect(url_for('reports.repair_history'))
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.repair_history'))

@reports_bp.route('/api/repair-history')
def api_repair_history():
    """API endpoint for the Repair Cost & History Report."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    provider_id = request.args.get('provider_id')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    year = request.args.get('year')
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": f"Invalid start_date format: {start_date}"}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": f"Invalid end_date format: {end_date}"}), 400
    
    # Convert provider_id to integer if it's a string
    if provider_id and provider_id.isdigit():
        provider_id = int(provider_id)
    elif provider_id:
        return jsonify({"error": f"Invalid provider_id: {provider_id}"}), 400
    
    # Convert year to integer if it's a string
    if year and year.isdigit():
        year = int(year)
    elif year:
        return jsonify({"error": f"Invalid year: {year}"}), 400
    
    # Create report instance
    try:
        report_class = get_report('repair_history')
        report = report_class(
            start_date=start_date,
            end_date=end_date,
            repair_type=repair_type,
            provider_id=provider_id,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            year=year
        )
        
        # Generate report data
        data = report.generate()
        
        # Return JSON response
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reports_bp.route('/test/repair-history')
def test_repair_history():
    """Development-only route for testing the Repair Cost & History Report without login."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    provider_id = request.args.get('provider_id')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    year = request.args.get('year')
    
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
    
    # Convert provider_id to integer if it's a string
    if provider_id and provider_id.isdigit():
        provider_id = int(provider_id)
    else:
        provider_id = None
    
    # Convert year to integer if it's a string
    if year and year.isdigit():
        year = int(year)
    else:
        year = None
    
    # Create report instance
    report_class = get_report('repair_history')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        repair_type=repair_type,
        provider_id=provider_id,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        year=year
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Check if there are any filters applied
        has_filters_applied = any([
            start_date, end_date, repair_type, 
            provider_id, vehicle_make, vehicle_model, year
        ])
        
        # Ensure all necessary parameters are included
        context = {
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
            'repair_type': repair_type,
            'provider_id': provider_id,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'year': year,
            'has_filters_applied': has_filters_applied,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/repair-history.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "repair_type": repair_type,
                "provider_id": provider_id,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "year": year
            }
        }), 500

@reports_bp.route('/parts-usage')
@login_required
def parts_usage():
    """Parts Usage Report - Analysis of part usage patterns, costs, and distribution."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    part_name = request.args.get('part_name')
    vehicle_model = request.args.get('vehicle_model')
    
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
    
    # Create report instance
    try:
        report_class = get_report('parts_usage')
        report = report_class(
            start_date=start_date,
            end_date=end_date,
            part_name=part_name,
            vehicle_model=vehicle_model
        )
        
        # Generate report data
        data = report.generate()
        
        # Render template with data
        return render_template('reports/parts-usage.html', report_data=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/parts-usage/export')
@login_required
def parts_usage_export():
    """Export Parts Usage Report to XLSX format."""
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    part_name = request.args.get('part_name')
    vehicle_model = request.args.get('vehicle_model')
    
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
    
    # Create report instance
    report_class = get_report('parts_usage')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        part_name=part_name,
        vehicle_model=vehicle_model
    )
    
    try:
        # Export to Excel
        excel_data = report.export_xlsx()
        
        # Prepare filename
        filename = f"parts_usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create response
        response = make_response(excel_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.parts_usage'))

@reports_bp.route('/api/parts-usage')
def api_parts_usage():
    """Parts Usage Report API endpoint."""
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    part_name = request.args.get('part_name')
    vehicle_model = request.args.get('vehicle_model')
    
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
    
    try:
        # Create report with all parameters
        report_class = get_report('parts_usage')
        report = report_class(
            start_date=start_date,
            end_date=end_date,
            part_name=part_name,
            vehicle_model=vehicle_model
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
            "message": "An error occurred while generating the parts usage report."
        }), 500

@reports_bp.route('/test/parts-usage')
def test_parts_usage():
    """Test endpoint for Parts Usage Report."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    part_name = request.args.get('part_name')
    vehicle_model = request.args.get('vehicle_model')
    
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
    
    # Create report instance
    report_class = get_report('parts_usage')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        part_name=part_name,
        vehicle_model=vehicle_model
    )
    
    # Generate report data without rendering template
    try:
        data = report.generate()
        # Add request parameters for debugging
        data["debug"] = {
            "start_date": request.args.get('start_date', '(not provided)'),
            "end_date": request.args.get('end_date', '(not provided)'),
            "part_name": request.args.get('part_name', '(not provided)'),
            "vehicle_model": request.args.get('vehicle_model', '(not provided)')
        }
        return jsonify(data)
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "error"
        }), 500

@reports_bp.route('/provider-efficiency')
@login_required
def provider_efficiency():
    """Provider Efficiency Report - Track repair provider performance metrics."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    
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
    
    # Create report instance
    try:
        report_class = get_report('provider_efficiency')
        report = report_class(
            start_date=start_date,
            end_date=end_date,
            repair_type=repair_type
        )
        
        # Generate report data
        data = report.generate()
        
        # Render template with data
        return render_template('reports/provider-efficiency.html', **data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/provider-efficiency/export')
@login_required
def provider_efficiency_export():
    """Export Provider Efficiency Report to XLSX format."""
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    
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
    
    # Create report instance
    report_class = get_report('provider_efficiency')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        repair_type=repair_type
    )
    
    try:
        # Export to Excel
        excel_data = report.export_xlsx()
        
        # Prepare filename
        filename = f"provider_efficiency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create response
        response = make_response(excel_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.provider_efficiency'))

@reports_bp.route('/api/provider-efficiency')
def api_provider_efficiency():
    """Provider Efficiency Report API endpoint."""
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
    
    try:
        # Create report with all parameters
        report_class = get_report('provider_efficiency')
        report = report_class(
            start_date=start_date,
            end_date=end_date,
            repair_type=repair_type
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
            "message": "An error occurred while generating the provider efficiency report."
        }), 500

@reports_bp.route('/test/provider-efficiency')
def test_provider_efficiency():
    """Test endpoint for Provider Efficiency Report."""
    # Get parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    repair_type = request.args.get('repair_type')
    
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
    
    # Create report instance
    report_class = get_report('provider_efficiency')
    report = report_class(
        start_date=start_date,
        end_date=end_date,
        repair_type=repair_type
    )
    
    # Generate report data without rendering template
    try:
        data = report.generate()
        # Add request parameters for debugging
        data["debug"] = {
            "start_date": request.args.get('start_date', '(not provided)'),
            "end_date": request.args.get('end_date', '(not provided)'),
            "repair_type": request.args.get('repair_type', '(not provided)')
        }
        return jsonify(data)
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "error"
        }), 500

@reports_bp.route('/profitability')
@login_required
def profitability():
    """Detailed Investment vs Profit Per Car Report."""
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_id = request.args.get('stand_id')
    dealer_id = request.args.get('dealer_id')
    
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
    
    # Convert stand_id and dealer_id to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
        
    if dealer_id and dealer_id.isdigit():
        dealer_id = int(dealer_id)
    else:
        dealer_id = None
    
    # Create report instance
    report_class = get_report('profitability')
    report = report_class(
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_id=stand_id,
        dealer_id=dealer_id
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'timeframe': timeframe,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'stand_id': stand_id,
            'dealer_id': dealer_id,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/profitability.html', **context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for('reports.index'))

@reports_bp.route('/profitability/export')
@login_required
def profitability_export():
    """Export Profitability Report data."""
    import xlsxwriter
    from io import BytesIO
    
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_id = request.args.get('stand_id')
    dealer_id = request.args.get('dealer_id')
    
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
    
    # Convert stand_id and dealer_id to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
        
    if dealer_id and dealer_id.isdigit():
        dealer_id = int(dealer_id)
    else:
        dealer_id = None
    
    # Create report instance
    report_class = get_report('profitability')
    report = report_class(
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_id=stand_id,
        dealer_id=dealer_id
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Create Excel workbook
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Format styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0d6efd',
            'color': 'white',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.0%',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })
        
        text_format = workbook.add_format({
            'border': 1
        })
        
        # ROI color band formats
        high_roi_format = workbook.add_format({
            'num_format': '0.0%',
            'bg_color': '#d1e7dd',  # Green background
            'border': 1
        })
        
        medium_roi_format = workbook.add_format({
            'num_format': '0.0%',
            'bg_color': '#fff3cd',  # Yellow background
            'border': 1
        })
        
        low_roi_format = workbook.add_format({
            'num_format': '0.0%',
            'bg_color': '#f8d7da',  # Red background
            'border': 1
        })
        
        # Add summary worksheet
        summary_sheet = workbook.add_worksheet('Summary')
        
        # Add report title and metadata
        summary_sheet.write(0, 0, 'Profitability Report', workbook.add_format({'bold': True, 'font_size': 14}))
        
        # Add filter information
        filter_row = 2
        summary_sheet.write(filter_row, 0, 'Filters:', workbook.add_format({'bold': True}))
        filter_row += 1
        
        summary_sheet.write(filter_row, 0, 'Time Range:')
        if timeframe == 'custom' and start_date and end_date:
            summary_sheet.write(filter_row, 1, f'Custom ({start_date} to {end_date})')
        else:
            timeframe_labels = {
                'last_30_days': 'Last 30 Days',
                'last_90_days': 'Last 90 Days',
                'year_to_date': 'Year to Date',
                'last_year': 'Last Year',
                'all_time': 'All Time'
            }
            summary_sheet.write(filter_row, 1, timeframe_labels.get(timeframe, timeframe))
        
        filter_row += 1
        
        if vehicle_make:
            summary_sheet.write(filter_row, 0, 'Make:')
            summary_sheet.write(filter_row, 1, vehicle_make)
            filter_row += 1
        
        if vehicle_model:
            summary_sheet.write(filter_row, 0, 'Model:')
            summary_sheet.write(filter_row, 1, vehicle_model)
            filter_row += 1
        
        if stand_id:
            stand_name = next((s.stand_name for s in data['available_stands'] if s.stand_id == stand_id), 'Unknown')
            summary_sheet.write(filter_row, 0, 'Stand:')
            summary_sheet.write(filter_row, 1, stand_name)
            filter_row += 1
        
        if dealer_id:
            dealer_name = next((d.dealer_name for d in data['available_dealers'] if d.dealer_id == dealer_id), 'Unknown')
            summary_sheet.write(filter_row, 0, 'Dealer:')
            summary_sheet.write(filter_row, 1, dealer_name)
            filter_row += 1
        
        # Add summary metrics
        summary_row = filter_row + 2
        summary_sheet.write(summary_row, 0, 'Summary Metrics:', workbook.add_format({'bold': True}))
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Total Cars Sold:')
        summary_sheet.write(summary_row, 1, data['total_cars_sold'])
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Total Revenue:')
        summary_sheet.write(summary_row, 1, float(data['total_revenue']), number_format)
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Total Investment:')
        summary_sheet.write(summary_row, 1, float(data['total_investment']), number_format)
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Total Profit:')
        summary_sheet.write(summary_row, 1, float(data['total_profit']), number_format)
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Average ROI:')
        summary_sheet.write(summary_row, 1, float(data['average_roi']) / 100, percent_format)
        summary_row += 1
        
        # Add ROI distribution
        summary_row += 2
        summary_sheet.write(summary_row, 0, 'ROI Distribution:', workbook.add_format({'bold': True}))
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'High ROI (≥30%):')
        summary_sheet.write(summary_row, 1, data['roi_distribution']['high'])
        summary_sheet.write(summary_row, 2, float(data['roi_distribution']['high_percent']) / 100, percent_format)
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Medium ROI (15-30%):')
        summary_sheet.write(summary_row, 1, data['roi_distribution']['medium'])
        summary_sheet.write(summary_row, 2, float(data['roi_distribution']['medium_percent']) / 100, percent_format)
        summary_row += 1
        
        summary_sheet.write(summary_row, 0, 'Low ROI (<15%):')
        summary_sheet.write(summary_row, 1, data['roi_distribution']['low'])
        summary_sheet.write(summary_row, 2, float(data['roi_distribution']['low_percent']) / 100, percent_format)
        
        # Add cars worksheet
        cars_sheet = workbook.add_worksheet('Cars')
        
        # Write headers
        headers = [
            'Make', 'Model', 'Year', 'VIN', 'Color', 'Stand', 'Dealer',
            'Purchase Price', 'Recon Cost', 'Refuel Cost', 'Total Investment',
            'Sale Price', 'Profit', 'ROI %', 'Sale Date'
        ]
        
        for col_num, header in enumerate(headers):
            cars_sheet.write(0, col_num, header, header_format)
        
        # Write car data
        for row_num, car in enumerate(data['cars_data']):
            row = row_num + 1
            
            cars_sheet.write(row, 0, car['make'], text_format)
            cars_sheet.write(row, 1, car['model'], text_format)
            cars_sheet.write(row, 2, car['year'], text_format)
            cars_sheet.write(row, 3, car['vin'], text_format)
            cars_sheet.write(row, 4, car['color'], text_format)
            cars_sheet.write(row, 5, car['stand_name'], text_format)
            cars_sheet.write(row, 6, car['dealer_name'], text_format)
            cars_sheet.write(row, 7, float(car['purchase_price']), number_format)
            cars_sheet.write(row, 8, float(car['repair_cost']), number_format)
            cars_sheet.write(row, 9, float(car['refuel_cost']), number_format)
            cars_sheet.write(row, 10, float(car['total_investment']), number_format)
            cars_sheet.write(row, 11, float(car['sale_price']), number_format)
            cars_sheet.write(row, 12, float(car['profit']), number_format)
            
            # Apply appropriate format based on ROI band
            roi_value = float(car['roi']) / 100
            if car['roi_band'] == 'high':
                cars_sheet.write(row, 13, roi_value, high_roi_format)
            elif car['roi_band'] == 'medium':
                cars_sheet.write(row, 13, roi_value, medium_roi_format)
            else:
                cars_sheet.write(row, 13, roi_value, low_roi_format)
            
            cars_sheet.write(row, 14, car['sale_date'], text_format)
        
        # Auto-adjust column widths
        for i, _ in enumerate(headers):
            col_width = 12
            if i < 7:  # Text columns
                col_width = 15
            cars_sheet.set_column(i, i, col_width)
        
        # Add models worksheet
        models_sheet = workbook.add_worksheet('Models')
        
        # Write headers
        model_headers = [
            'Make', 'Model', 'Count', 
            'Avg Purchase', 'Avg Recon', 'Avg Refuel', 'Avg Investment',
            'Avg Sale Price', 'Avg Profit', 'ROI %'
        ]
        
        for col_num, header in enumerate(model_headers):
            models_sheet.write(0, col_num, header, header_format)
        
        # Write model data
        for row_num, model in enumerate(data['model_profitability']):
            row = row_num + 1
            
            models_sheet.write(row, 0, model['make'], text_format)
            models_sheet.write(row, 1, model['model'], text_format)
            models_sheet.write(row, 2, model['count'], text_format)
            models_sheet.write(row, 3, float(model['avg_purchase']), number_format)
            models_sheet.write(row, 4, float(model['avg_repair']), number_format)
            models_sheet.write(row, 5, float(model['avg_refuel']), number_format)
            models_sheet.write(row, 6, float(model['avg_investment']), number_format)
            models_sheet.write(row, 7, float(model['avg_revenue']), number_format)
            models_sheet.write(row, 8, float(model['avg_profit']), number_format)
            
            # Apply appropriate format based on ROI band
            roi_value = float(model['roi']) / 100
            if model['roi_band'] == 'high':
                models_sheet.write(row, 9, roi_value, high_roi_format)
            elif model['roi_band'] == 'medium':
                models_sheet.write(row, 9, roi_value, medium_roi_format)
            else:
                models_sheet.write(row, 9, roi_value, low_roi_format)
        
        # Auto-adjust column widths
        for i, _ in enumerate(model_headers):
            col_width = 12
            if i < 3:  # Text columns
                col_width = 15
            models_sheet.set_column(i, i, col_width)
        
        # Close workbook
        workbook.close()
        
        # Prepare response
        output.seek(0)
        
        # Generate filename with date and filters
        filename_parts = ['Profitability_Report']
        
        if vehicle_make:
            filename_parts.append(vehicle_make.replace(' ', '_'))
            
            if vehicle_model:
                filename_parts.append(vehicle_model.replace(' ', '_'))
        
        if timeframe == 'custom' and start_date and end_date:
            filename_parts.append(f"{start_date}_to_{end_date}")
        else:
            filename_parts.append(timeframe.replace('_', '-'))
        
        filename = '_'.join(filename_parts) + '.xlsx'
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.profitability'))

@reports_bp.route('/api/profitability')
def api_profitability():
    """API endpoint for Profitability Report data."""
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_id = request.args.get('stand_id')
    dealer_id = request.args.get('dealer_id')
    
    # Convert date strings to date objects if provided
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end date format'}), 400
    
    # Convert stand_id and dealer_id to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
        
    if dealer_id and dealer_id.isdigit():
        dealer_id = int(dealer_id)
    else:
        dealer_id = None
    
    # Create report instance
    try:
        report_class = get_report('profitability')
        report = report_class(
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            stand_id=stand_id,
            dealer_id=dealer_id
        )
        
        # Generate report data
        data = report.generate()
        
        # Convert data for JSON serialization
        from app.utils.serializers import decimal_to_float
        serialized_data = decimal_to_float(data)
        
        return jsonify(serialized_data)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "timeframe": timeframe,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "stand_id": stand_id,
                "dealer_id": dealer_id
            }
        }), 500

@reports_bp.route('/test/profitability')
def test_profitability():
    """Development-only route for testing the Profitability Report without login."""
    # Get parameters from request
    timeframe = request.args.get('timeframe', 'last_30_days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_make = request.args.get('vehicle_make')
    vehicle_model = request.args.get('vehicle_model')
    stand_id = request.args.get('stand_id')
    dealer_id = request.args.get('dealer_id')
    
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
    
    # Convert stand_id and dealer_id to integers if provided
    if stand_id and stand_id.isdigit():
        stand_id = int(stand_id)
    else:
        stand_id = None
        
    if dealer_id and dealer_id.isdigit():
        dealer_id = int(dealer_id)
    else:
        dealer_id = None
    
    # Create report instance
    report_class = get_report('profitability')
    report = report_class(
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        stand_id=stand_id,
        dealer_id=dealer_id
    )
    
    try:
        # Generate report data
        data = report.generate()
        
        # Ensure all necessary parameters are included
        context = {
            'timeframe': timeframe,
            'current_year': datetime.now().year,
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'stand_id': stand_id,
            'dealer_id': dealer_id,
            **data
        }
        
        # Render template with complete context
        return render_template('reports/profitability.html', **context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "parameters": {
                "timeframe": timeframe,
                "start_date": start_date,
                "end_date": end_date,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "stand_id": stand_id,
                "dealer_id": dealer_id
            }
        }), 500
