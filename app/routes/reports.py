from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import db
from app.models.car import Car
from app.models.repair import Repair
from app.models.repair_provider import RepairProvider
from app.models.dealer import Dealer
from app.models.stand import Stand
from sqlalchemy import func, extract, text, desc, asc
from datetime import datetime, date, timedelta
import calendar
from collections import defaultdict

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
    """
    Sales Performance Report - Shows sales data by period (daily, weekly, monthly, yearly)
    with metrics on revenue, profit, and dealer performance.
    """
    # Get request parameters with defaults
    period = request.args.get('period', 'monthly')
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', 0))  # 0 means all months
    
    # Query sold cars within the specified time period
    query = Car.query.filter(Car.sold == True)
    
    # Apply year filter
    query = query.filter(extract('year', Car.date_sold) == year)
    
    # Apply month filter if specified
    if month > 0 and period != 'yearly':
        query = query.filter(extract('month', Car.date_sold) == month)
    
    # Get all sold cars for the period
    sold_cars = query.all()
    
    # Prepare period-specific data
    period_labels = []
    sales_by_period = []
    sales_counts = []
    revenues = []
    profits = []
    
    # Set period-specific variables
    if period == 'yearly':
        period_name = 'Year'
        period_label = 'Year'
        # Get yearly data for multiple years
        years = range(year-4, year+1)  # Last 5 years including current
        
        # For each year, collect sales data
        for y in years:
            yearly_cars = [car for car in sold_cars if car.date_sold.year == y]
            if not yearly_cars:
                continue
                
            count = len(yearly_cars)
            revenue = sum(car.sale_price for car in yearly_cars)
            profit = sum(car.profit for car in yearly_cars)
            avg_price = revenue / count if count else 0
            margin = (profit / revenue * 100) if revenue else 0
            
            # Calculate trend compared to previous year
            prev_year_cars = Car.query.filter(Car.sold == True, 
                                             extract('year', Car.date_sold) == y-1).all()
            prev_count = len(prev_year_cars)
            trend = ((count - prev_count) / prev_count * 100) if prev_count else 0
            
            period_labels.append(str(y))
            sales_counts.append(count)
            revenues.append(revenue)
            profits.append(profit)
            
            sales_by_period.append({
                'label': str(y),
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
    
    elif period == 'monthly':
        period_name = 'Month'
        period_label = 'Month'
        # Get monthly data
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for m in range(1, 13):
            monthly_cars = [car for car in sold_cars if car.date_sold.month == m]
            if not monthly_cars and month > 0:  # Skip empty months if specific month selected
                continue
                
            count = len(monthly_cars)
            revenue = sum(car.sale_price for car in monthly_cars)
            profit = sum(car.profit for car in monthly_cars)
            avg_price = revenue / count if count else 0
            margin = (profit / revenue * 100) if revenue else 0
            
            # Calculate trend compared to previous month
            prev_month = m - 1 if m > 1 else 12
            prev_year = year if m > 1 else year - 1
            prev_month_cars = Car.query.filter(Car.sold == True, 
                                             extract('year', Car.date_sold) == prev_year,
                                             extract('month', Car.date_sold) == prev_month).all()
            prev_count = len(prev_month_cars)
            trend = ((count - prev_count) / prev_count * 100) if prev_count else 0
            
            period_labels.append(month_names[m-1])
            sales_counts.append(count)
            revenues.append(revenue)
            profits.append(profit)
            
            sales_by_period.append({
                'label': month_names[m-1],
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
    
    elif period == 'weekly':
        period_name = 'Week'
        period_label = 'Week Number'
        # Group by week of year
        weeks = {}
        
        for car in sold_cars:
            week_num = car.date_sold.isocalendar()[1]  # ISO week number
            if week_num not in weeks:
                weeks[week_num] = {'cars': [], 'count': 0, 'revenue': 0, 'profit': 0}
            
            weeks[week_num]['cars'].append(car)
            weeks[week_num]['count'] += 1
            weeks[week_num]['revenue'] += car.sale_price
            weeks[week_num]['profit'] += car.profit
        
        # Sort weeks by week number
        sorted_weeks = sorted(weeks.items())
        
        for week_num, data in sorted_weeks:
            count = data['count']
            revenue = data['revenue']
            profit = data['profit']
            avg_price = revenue / count if count else 0
            margin = (profit / revenue * 100) if revenue else 0
            
            # Calculate trend (simplified for weekly)
            prev_week = week_num - 1
            trend = 0
            if prev_week in weeks:
                prev_count = weeks[prev_week]['count']
                trend = ((count - prev_count) / prev_count * 100) if prev_count else 0
            
            period_labels.append(f"Week {week_num}")
            sales_counts.append(count)
            revenues.append(revenue)
            profits.append(profit)
            
            sales_by_period.append({
                'label': f"Week {week_num}",
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
    
    elif period == 'daily':
        period_name = 'Day'
        period_label = 'Date'
        # Filter to specific month if provided
        if month > 0:
            filtered_cars = [car for car in sold_cars if car.date_sold.month == month]
        else:
            filtered_cars = sold_cars
        
        # Group by day
        days = {}
        for car in filtered_cars:
            day_key = car.date_sold.strftime('%Y-%m-%d')
            if day_key not in days:
                days[day_key] = {'cars': [], 'count': 0, 'revenue': 0, 'profit': 0}
            
            days[day_key]['cars'].append(car)
            days[day_key]['count'] += 1
            days[day_key]['revenue'] += car.sale_price
            days[day_key]['profit'] += car.profit
        
        # Sort days by date
        sorted_days = sorted(days.items())
        
        for day_key, data in sorted_days:
            day_date = datetime.strptime(day_key, '%Y-%m-%d')
            count = data['count']
            revenue = data['revenue']
            profit = data['profit']
            avg_price = revenue / count if count else 0
            margin = (profit / revenue * 100) if revenue else 0
            
            # Calculate trend compared to previous day
            prev_day = (day_date - timedelta(days=1)).strftime('%Y-%m-%d')
            trend = 0
            if prev_day in days:
                prev_count = days[prev_day]['count']
                trend = ((count - prev_count) / prev_count * 100) if prev_count else 0
            
            # Format day label based on date
            day_label = day_date.strftime('%d %b')
            
            period_labels.append(day_label)
            sales_counts.append(count)
            revenues.append(revenue)
            profits.append(profit)
            
            sales_by_period.append({
                'label': day_label,
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })

    # Calculate summary metrics
    total_sales = len(sold_cars)
    total_revenue = sum(car.sale_price for car in sold_cars)
    total_profit = sum(car.profit for car in sold_cars)
    avg_price = total_revenue / total_sales if total_sales else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    
    # Get dealer performance data
    dealer_performance = []
    dealer_names = []
    dealer_revenues = []
    
    dealers = Dealer.query.all()
    for dealer in dealers:
        dealer_cars = [car for car in sold_cars if car.dealer_id == dealer.dealer_id]
        if not dealer_cars:
            continue
            
        sales_count = len(dealer_cars)
        revenue = sum(car.sale_price for car in dealer_cars)
        profit = sum(car.profit for car in dealer_cars)
        commission = sum(car.commission for car in dealer_cars)
        
        avg_price = revenue / sales_count if sales_count else 0
        avg_profit = profit / sales_count if sales_count else 0
        margin = (profit / revenue * 100) if revenue else 0
        percentage = (sales_count / total_sales * 100) if total_sales else 0
        
        dealer_performance.append({
            'name': dealer.name,
            'sales_count': sales_count,
            'revenue': revenue,
            'profit': profit,
            'avg_price': avg_price,
            'avg_profit': avg_profit,
            'margin': margin,
            'percentage': percentage,
            'commission': commission
        })
        
        dealer_names.append(dealer.name)
        dealer_revenues.append(revenue)
    
    # Sort dealer performance by sales count (descending)
    dealer_performance.sort(key=lambda x: x['sales_count'], reverse=True)
    
    # Convert to JSON-safe values for the template
    dealer_names = [d.name for d in dealers if d.name in dealer_names]
    
    return render_template(
        'reports/sales_performance.html',
        period=period,
        period_name=period_name,
        period_label=period_label,
        year=year,
        month=month,
        current_year=datetime.now().year,
        total_sales=total_sales,
        total_revenue=total_revenue,
        total_profit=total_profit,
        avg_price=avg_price,
        profit_margin=profit_margin,
        sales_by_period=sales_by_period,
        period_labels=period_labels,
        sales_counts=sales_counts,
        revenues=revenues,
        profits=profits,
        dealer_performance=dealer_performance,
        dealer_names=dealer_names,
        dealer_revenues=dealer_revenues,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

@reports_bp.route('/repair-analysis')
@login_required
def repair_analysis():
    """
    Repair Cost Analysis Report - Shows repair costs by type and provider,
    repair duration, and monthly repair costs trends.
    """
    # Get request parameters
    year = int(request.args.get('year', datetime.now().year))
    
    # Query repairs within the specified year
    repairs = Repair.query.filter(
        extract('year', Repair.start_date) == year
    ).all()
    
    # Calculate total metrics
    total_repairs = len(repairs)
    total_cost = sum(repair.repair_cost for repair in repairs)
    avg_cost_per_repair = total_cost / total_repairs if total_repairs else 0
    
    # Repair costs by type
    repair_types = {}
    for repair in repairs:
        if repair.repair_type not in repair_types:
            repair_types[repair.repair_type] = {
                'count': 0, 
                'total_cost': 0
            }
        repair_types[repair.repair_type]['count'] += 1
        repair_types[repair.repair_type]['total_cost'] += repair.repair_cost
    
    repair_by_type = []
    for rtype, data in repair_types.items():
        count = data['count']
        total_cost = data['total_cost']
        avg_cost = total_cost / count if count else 0
        
        repair_by_type.append({
            'repair_type': rtype,
            'count': count,
            'total_cost': total_cost,
            'avg_cost': avg_cost
        })
    
    # Sort by total cost (descending)
    repair_by_type.sort(key=lambda x: x['total_cost'], reverse=True)
    
    # Repair costs by provider
    repair_providers = {}
    for repair in repairs:
        provider_id = repair.provider_id
        provider = RepairProvider.query.get(provider_id)
        provider_name = provider.name if provider else 'Unknown'
        
        if provider_name not in repair_providers:
            repair_providers[provider_name] = {
                'count': 0, 
                'total_cost': 0
            }
        repair_providers[provider_name]['count'] += 1
        repair_providers[provider_name]['total_cost'] += repair.repair_cost
    
    repair_by_provider = []
    for provider_name, data in repair_providers.items():
        count = data['count']
        total_cost = data['total_cost']
        avg_cost = total_cost / count if count else 0
        
        repair_by_provider.append({
            'provider_name': provider_name,
            'count': count,
            'total_cost': total_cost,
            'avg_cost': avg_cost
        })
    
    # Sort by total cost (descending)
    repair_by_provider.sort(key=lambda x: x['total_cost'], reverse=True)
    
    # Calculate average repair duration by type
    repair_duration = []
    for rtype, data in repair_types.items():
        type_repairs = [r for r in repairs if r.repair_type == rtype]
        total_days = sum(r.duration_days for r in type_repairs)
        avg_days = total_days / len(type_repairs) if type_repairs else 0
        
        repair_duration.append({
            'repair_type': rtype,
            'avg_days': avg_days
        })
    
    # Sort by average duration (descending)
    repair_duration.sort(key=lambda x: x['avg_days'], reverse=True)
    
    # Monthly repair costs
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_costs = defaultdict(float)
    for repair in repairs:
        month_idx = repair.start_date.month - 1
        monthly_costs[month_idx] += repair.repair_cost
    
    costs = [monthly_costs.get(m, 0) for m in range(12)]
    
    return render_template(
        'reports/repair_analysis.html',
        year=year,
        current_year=datetime.now().year,
        total_repairs=total_repairs,
        total_cost=total_cost,
        avg_cost_per_repair=avg_cost_per_repair,
        repair_by_type=repair_by_type,
        repair_by_provider=repair_by_provider,
        repair_duration=repair_duration,
        months=months,
        costs=costs,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

@reports_bp.route('/inventory-aging')
@login_required
def inventory_aging():
    """
    Inventory Aging Report - Shows aging of current inventory, categorizing
    cars based on how long they've been in stock with investment tracking.
    """
    # Get request parameters
    status = request.args.get('status', 'all')
    
    # Query current inventory (unsold cars)
    query = Car.query.filter(Car.sold == False)
    
    # Apply status filter if specified
    if status != 'all':
        query = query.filter(Car.status == status)
    
    # Get all inventory cars
    inventory_cars = query.all()
    
    # Calculate total metrics
    total_inventory = len(inventory_cars)
    total_investment = sum(car.total_investment for car in inventory_cars)
    avg_investment_per_vehicle = total_investment / total_inventory if total_inventory else 0
    
    # Calculate days in inventory for each car
    for car in inventory_cars:
        # If car.days_in_inventory property doesn't exist, calculate it
        if not hasattr(car, 'days_in_inventory') or not car.days_in_inventory:
            purchase_date = car.purchase_date
            today = datetime.now().date()
            delta = today - purchase_date
            car.days_in_inventory = delta.days
    
    # Calculate average days in inventory
    total_days = sum(car.days_in_inventory for car in inventory_cars)
    avg_days_in_inventory = total_days / total_inventory if total_inventory else 0
    
    # Define aging buckets
    aging_buckets = [
        {'min': 0, 'max': 15, 'label': '0-15 Days', 'alert': False},
        {'min': 16, 'max': 30, 'label': '16-30 Days', 'alert': False},
        {'min': 31, 'max': 45, 'label': '31-45 Days', 'alert': False},
        {'min': 46, 'max': 60, 'label': '46-60 Days', 'alert': True},
        {'min': 61, 'max': 999, 'label': '61+ Days', 'alert': True}
    ]
    
    # Count cars in each bucket
    for bucket in aging_buckets:
        bucket_cars = [
            car for car in inventory_cars 
            if bucket['min'] <= car.days_in_inventory <= bucket['max']
        ]
        bucket['count'] = len(bucket_cars)
        bucket['investment'] = sum(car.total_investment for car in bucket_cars)
        bucket['avg_investment'] = bucket['investment'] / bucket['count'] if bucket['count'] else 0
        bucket['percentage'] = (bucket['count'] / total_inventory * 100) if total_inventory else 0
    
    # Count aged vehicles (> 45 days)
    aged_vehicle_count = sum(
        bucket['count'] for bucket in aging_buckets 
        if bucket['min'] >= 46
    )
    aged_vehicle_percentage = (aged_vehicle_count / total_inventory * 100) if total_inventory else 0
    
    # Count cars by status
    status_counts = {
        'reconditioning': len([car for car in inventory_cars if car.status == 'reconditioning']),
        'ready': len([car for car in inventory_cars if car.status == 'ready']),
        'stand': len([car for car in inventory_cars if car.status == 'stand'])
    }
    
    return render_template(
        'reports/inventory_aging.html',
        status=status,
        total_inventory=total_inventory,
        avg_days_in_inventory=avg_days_in_inventory,
        total_investment=total_investment,
        avg_investment_per_vehicle=avg_investment_per_vehicle,
        aged_vehicle_count=aged_vehicle_count,
        aged_vehicle_percentage=aged_vehicle_percentage,
        aging_buckets=aging_buckets,
        status_counts=status_counts,
        cars=inventory_cars,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

@reports_bp.route('/profit-margin')
@login_required
def profit_margin():
    """
    Profit Margin Analysis Report - Shows profit margins for sold cars,
    categorizing them into buckets based on profit percentage.
    """
    # Get request parameters
    year = int(request.args.get('year', datetime.now().year))
    sort = request.args.get('sort', 'profit_desc')
    
    # Query sold cars within the specified year
    sold_cars = Car.query.filter(
        Car.sold == True,
        extract('year', Car.date_sold) == year
    )
    
    # Apply sorting
    if sort == 'profit_desc':
        sold_cars = sold_cars.order_by(desc(Car.date_sold))
    elif sort == 'profit_asc':
        sold_cars = sold_cars.order_by(asc(Car.date_sold))
    elif sort == 'margin_desc':
        # Sort by margin percentage (profit / sale_price)
        sold_cars = sold_cars.order_by(desc(Car.profit / Car.sale_price))
    elif sort == 'margin_asc':
        sold_cars = sold_cars.order_by(asc(Car.profit / Car.sale_price))
    elif sort == 'date_desc':
        sold_cars = sold_cars.order_by(desc(Car.date_sold))
    elif sort == 'date_asc':
        sold_cars = sold_cars.order_by(asc(Car.date_sold))
    
    # Get all sorted cars
    cars = sold_cars.all()
    
    # Calculate total metrics
    total_cars_sold = len(cars)
    total_revenue = sum(car.sale_price for car in cars)
    total_cost = sum(car.total_cost for car in cars)
    total_profit = sum(car.profit for car in cars)
    avg_profit = total_profit / total_cars_sold if total_cars_sold else 0
    avg_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    
    # Calculate margin for each car
    for car in cars:
        # If car.margin property doesn't exist, calculate it
        if not hasattr(car, 'margin') or car.margin is None:
            car.margin = (car.profit / car.sale_price * 100) if car.sale_price else 0
    
    # Define margin buckets
    margin_buckets = [
        {
            'min': -999, 'max': 0, 
            'label': 'Loss (< 0%)', 
            'class': 'table-danger',
            'badge_class': 'bg-danger',
            'performance': 'Loss',
            'color': 'rgba(220, 53, 69, 0.7)'
        },
        {
            'min': 0, 'max': 5, 
            'label': 'Low (0-5%)', 
            'class': 'table-warning',
            'badge_class': 'bg-warning text-dark',
            'performance': 'Poor',
            'color': 'rgba(255, 193, 7, 0.7)'
        },
        {
            'min': 5, 'max': 10, 
            'label': 'Medium (5-10%)', 
            'class': '',
            'badge_class': 'bg-secondary',
            'performance': 'Average',
            'color': 'rgba(108, 117, 125, 0.7)'
        },
        {
            'min': 10, 'max': 15, 
            'label': 'Good (10-15%)', 
            'class': 'table-info',
            'badge_class': 'bg-info',
            'performance': 'Good',
            'color': 'rgba(23, 162, 184, 0.7)'
        },
        {
            'min': 15, 'max': 999, 
            'label': 'Excellent (15%+)', 
            'class': 'table-success',
            'badge_class': 'bg-success',
            'performance': 'Excellent',
            'color': 'rgba(40, 167, 69, 0.7)'
        }
    ]
    
    # Count cars in each bucket
    for bucket in margin_buckets:
        bucket_cars = [
            car for car in cars 
            if bucket['min'] <= car.margin < bucket['max']
        ]
        bucket['count'] = len(bucket_cars)
        bucket['revenue'] = sum(car.sale_price for car in bucket_cars)
        bucket['cost'] = sum(car.total_cost for car in bucket_cars)
        bucket['profit'] = sum(car.profit for car in bucket_cars)
        bucket['avg_profit'] = bucket['profit'] / bucket['count'] if bucket['count'] else 0
        bucket['percentage'] = (bucket['count'] / total_cars_sold * 100) if total_cars_sold else 0
    
    # Get monthly profit trends
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    monthly_profits = [0] * 12
    monthly_revenues = [0] * 12
    
    for car in cars:
        month_idx = car.date_sold.month - 1
        monthly_profits[month_idx] += car.profit
        monthly_revenues[month_idx] += car.sale_price
    
    # Analyze profitability by make/model
    model_analysis = {}
    for car in cars:
        model_key = car.vehicle_name
        
        if model_key not in model_analysis:
            model_analysis[model_key] = {
                'count': 0,
                'total_price': 0,
                'total_cost': 0,
                'total_profit': 0
            }
        
        model_analysis[model_key]['count'] += 1
        model_analysis[model_key]['total_price'] += car.sale_price
        model_analysis[model_key]['total_cost'] += car.total_cost
        model_analysis[model_key]['total_profit'] += car.profit
    
    # Calculate averages and format for template
    model_data = []
    for name, data in model_analysis.items():
        if data['count'] >= 2:  # Only include models with at least 2 sales
            avg_price = data['total_price'] / data['count']
            avg_cost = data['total_cost'] / data['count']
            avg_profit = data['total_profit'] / data['count']
            avg_margin = (avg_profit / avg_price * 100) if avg_price else 0
            
            model_data.append({
                'name': name,
                'count': data['count'],
                'avg_price': avg_price,
                'avg_cost': avg_cost,
                'avg_profit': avg_profit,
                'avg_margin': avg_margin
            })
    
    # Sort by average profit margin (descending)
    model_data.sort(key=lambda x: x['avg_margin'], reverse=True)
    
    return render_template(
        'reports/profit_margin.html',
        year=year,
        current_year=datetime.now().year,
        sort=sort,
        total_cars_sold=total_cars_sold,
        total_revenue=total_revenue,
        total_cost=total_cost,
        total_profit=total_profit,
        avg_profit=avg_profit,
        avg_margin=avg_margin,
        margin_buckets=margin_buckets,
        months=months,
        monthly_profits=monthly_profits,
        monthly_revenues=monthly_revenues,
        model_analysis=model_data,
        cars=cars,
        report_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    ) 