from app.reports.base.report import Report
from app.models.car import Car
from sqlalchemy import extract, func, desc, asc
from datetime import datetime

class ProfitMarginReport(Report):
    """
    Profit Margin Analysis Report - Shows profit margins for sold cars,
    categorizing them into buckets based on profit percentage.
    """
    
    template_path = 'reports/profit-margin.html'
    
    param_rules = {
        'year': (int, False, lambda: datetime.now().year),
        'sort': (str, False, 'profit_desc', lambda x: x in ['profit_desc', 'profit_asc', 'margin_desc', 'margin_asc', 'date_desc', 'date_asc'])
    }
    
    def __init__(self):
        super().__init__()
        self.data = {
            'current_year': datetime.now().year,
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        }
    
    def generate(self):
        """Generate the profit margin report data"""
        # Extract validated parameters
        year = self.params['year']
        sort = self.params['sort']
        
        # Query sold cars within the specified year
        cars = self._get_sorted_cars(year, sort)
        
        # Calculate total metrics
        total_cars_sold = len(cars)
        total_revenue = sum(car.sale_price for car in cars)
        total_cost = sum(car.total_cost for car in cars)
        total_profit = sum(car.profit for car in cars)
        avg_profit = total_profit / total_cars_sold if total_cars_sold else 0
        avg_margin = (total_profit / total_revenue * 100) if total_revenue else 0
        
        # Calculate margin for each car
        self._calculate_margins(cars)
        
        # Define and populate margin buckets
        margin_buckets = self._get_margin_buckets(cars, total_cars_sold)
        
        # Get monthly trends
        monthly_profits, monthly_revenues = self._get_monthly_trends(cars)
        
        # Analyze profitability by make/model
        model_data = self._get_model_analysis(cars)
        
        # Update data dictionary
        self.data.update({
            'total_cars_sold': total_cars_sold,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'avg_profit': avg_profit,
            'avg_margin': avg_margin,
            'margin_buckets': margin_buckets,
            'monthly_profits': monthly_profits,
            'monthly_revenues': monthly_revenues,
            'model_analysis': model_data,
            'cars': cars
        })
    
    def _get_sorted_cars(self, year, sort):
        """Get sorted cars based on specified criteria"""
        query = Car.query.filter(
            Car.sold == True,
            extract('year', Car.date_sold) == year
        )
        
        # Apply sorting
        if sort == 'profit_desc':
            query = query.order_by(desc(Car.date_sold))
        elif sort == 'profit_asc':
            query = query.order_by(asc(Car.date_sold))
        elif sort == 'margin_desc':
            # Sort by margin percentage (profit / sale_price)
            query = query.order_by(desc(Car.profit / Car.sale_price))
        elif sort == 'margin_asc':
            query = query.order_by(asc(Car.profit / Car.sale_price))
        elif sort == 'date_desc':
            query = query.order_by(desc(Car.date_sold))
        elif sort == 'date_asc':
            query = query.order_by(asc(Car.date_sold))
        
        return query.all()
    
    def _calculate_margins(self, cars):
        """Calculate margin for each car"""
        for car in cars:
            # If car.margin property doesn't exist, calculate it
            if not hasattr(car, 'margin') or car.margin is None:
                car.margin = (car.profit / car.sale_price * 100) if car.sale_price else 0
    
    def _get_margin_buckets(self, cars, total_cars_sold):
        """Define and populate margin buckets"""
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
        
        return margin_buckets
    
    def _get_monthly_trends(self, cars):
        """Get monthly profit trends"""
        monthly_profits = [0] * 12
        monthly_revenues = [0] * 12
        
        for car in cars:
            month_idx = car.date_sold.month - 1
            monthly_profits[month_idx] += car.profit
            monthly_revenues[month_idx] += car.sale_price
        
        return monthly_profits, monthly_revenues
    
    def _get_model_analysis(self, cars):
        """Analyze profitability by make/model"""
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
        
        return model_data 