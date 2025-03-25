from app.reports.base.report import Report
from app.models.car import Car
from app.models.dealer import Dealer
from sqlalchemy import extract, func
from datetime import datetime, timedelta
import calendar
from collections import defaultdict

class SalesPerformanceReport(Report):
    """
    Sales Performance Report - Shows sales data by period (daily, weekly, monthly, yearly)
    with metrics on revenue, profit, and dealer performance.
    """
    
    template_path = 'reports/sales-performance.html'
    
    param_rules = {
        'period': (str, False, 'monthly', lambda x: x in ['daily', 'weekly', 'monthly', 'yearly']),
        'year': (int, False, lambda: datetime.now().year),
        'month': (int, False, 0, lambda x: 0 <= x <= 12)
    }
    
    def __init__(self):
        super().__init__()
        self.data = {
            'current_year': datetime.now().year,
            'period_labels': [],
            'sales_counts': [],
            'revenues': [],
            'profits': [],
            'dealer_names': [],
            'dealer_revenues': []
        }
    
    def generate(self):
        """Generate the sales performance report data"""
        # Extract validated parameters
        period = self.params['period']
        year = self.params['year']
        month = self.params['month']  # 0 means all months
        
        # Query sold cars within the specified time period
        query = Car.query.filter(Car.sold == True)
        
        # Apply year filter
        query = query.filter(extract('year', Car.date_sold) == year)
        
        # Apply month filter if specified
        if month > 0 and period != 'yearly':
            query = query.filter(extract('month', Car.date_sold) == month)
        
        # Get all sold cars for the period
        sold_cars = query.all()
        
        # Set period-specific variables
        period_name, period_label = self._get_period_labels(period)
        
        # Generate period-specific data
        sales_by_period = self._generate_period_data(period, year, month, sold_cars)
        
        # Calculate summary metrics
        total_sales = len(sold_cars)
        total_revenue = sum(car.sale_price for car in sold_cars)
        total_profit = sum(car.profit for car in sold_cars)
        avg_price = total_revenue / total_sales if total_sales else 0
        profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
        
        # Get dealer performance data
        dealer_performance, dealer_names, dealer_revenues = self._get_dealer_performance(sold_cars, total_sales)
        
        # Update data dictionary with generated values
        self.data.update({
            'period_name': period_name,
            'period_label': period_label,
            'sales_by_period': sales_by_period,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'avg_price': avg_price,
            'profit_margin': profit_margin,
            'dealer_performance': dealer_performance,
            'dealer_names': dealer_names,
            'dealer_revenues': dealer_revenues
        })
    
    def _get_period_labels(self, period):
        """Get period-specific labels"""
        if period == 'yearly':
            return 'Year', 'Year'
        elif period == 'monthly':
            return 'Month', 'Month'
        elif period == 'weekly':
            return 'Week', 'Week Number'
        elif period == 'daily':
            return 'Day', 'Date'
        
        return 'Period', 'Period'
    
    def _generate_period_data(self, period, year, month, sold_cars):
        """Generate data for the specified period"""
        if period == 'yearly':
            return self._generate_yearly_data(year, sold_cars)
        elif period == 'monthly':
            return self._generate_monthly_data(sold_cars)
        elif period == 'weekly':
            return self._generate_weekly_data(sold_cars)
        elif period == 'daily':
            return self._generate_daily_data(month, sold_cars)
        
        return []
    
    def _generate_yearly_data(self, year, sold_cars):
        """Generate yearly sales data"""
        sales_by_period = []
        years = range(year-4, year+1)  # Last 5 years including current
        
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
            
            self.data['period_labels'].append(str(y))
            self.data['sales_counts'].append(count)
            self.data['revenues'].append(revenue)
            self.data['profits'].append(profit)
            
            sales_by_period.append({
                'label': str(y),
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
        
        return sales_by_period
    
    def _generate_monthly_data(self, sold_cars):
        """Generate monthly sales data"""
        sales_by_period = []
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for m in range(1, 13):
            monthly_cars = [car for car in sold_cars if car.date_sold.month == m]
            if not monthly_cars and self.params['month'] > 0:  # Skip empty months if specific month selected
                continue
                
            count = len(monthly_cars)
            revenue = sum(car.sale_price for car in monthly_cars)
            profit = sum(car.profit for car in monthly_cars)
            avg_price = revenue / count if count else 0
            margin = (profit / revenue * 100) if revenue else 0
            
            # Calculate trend compared to previous month
            prev_month = m - 1 if m > 1 else 12
            prev_year = self.params['year'] if m > 1 else self.params['year'] - 1
            prev_month_cars = Car.query.filter(Car.sold == True, 
                                            extract('year', Car.date_sold) == prev_year,
                                            extract('month', Car.date_sold) == prev_month).all()
            prev_count = len(prev_month_cars)
            trend = ((count - prev_count) / prev_count * 100) if prev_count else 0
            
            self.data['period_labels'].append(month_names[m-1])
            self.data['sales_counts'].append(count)
            self.data['revenues'].append(revenue)
            self.data['profits'].append(profit)
            
            sales_by_period.append({
                'label': month_names[m-1],
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
        
        return sales_by_period
    
    def _generate_weekly_data(self, sold_cars):
        """Generate weekly sales data"""
        sales_by_period = []
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
            
            self.data['period_labels'].append(f"Week {week_num}")
            self.data['sales_counts'].append(count)
            self.data['revenues'].append(revenue)
            self.data['profits'].append(profit)
            
            sales_by_period.append({
                'label': f"Week {week_num}",
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
        
        return sales_by_period
    
    def _generate_daily_data(self, month, sold_cars):
        """Generate daily sales data"""
        sales_by_period = []
        
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
            
            self.data['period_labels'].append(day_label)
            self.data['sales_counts'].append(count)
            self.data['revenues'].append(revenue)
            self.data['profits'].append(profit)
            
            sales_by_period.append({
                'label': day_label,
                'count': count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'margin': margin,
                'trend': trend
            })
        
        return sales_by_period
    
    def _get_dealer_performance(self, sold_cars, total_sales):
        """Get dealer performance metrics"""
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
                'name': dealer.dealer_name,
                'sales_count': sales_count,
                'revenue': revenue,
                'profit': profit,
                'avg_price': avg_price,
                'avg_profit': avg_profit,
                'margin': margin,
                'percentage': percentage,
                'commission': commission
            })
            
            dealer_names.append(dealer.dealer_name)
            dealer_revenues.append(revenue)
        
        # Sort dealer performance by sales count (descending)
        dealer_performance.sort(key=lambda x: x['sales_count'], reverse=True)
        
        # Convert to JSON-safe values for the template
        dealer_names = [d.dealer_name for d in dealers if d.dealer_name in dealer_names]
        
        return dealer_performance, dealer_names, dealer_revenues 