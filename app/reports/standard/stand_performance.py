from app.reports.base import Report
from app.models import Car, Sale, Stand, Setting
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.sql import text
import decimal
from dateutil.relativedelta import relativedelta
from collections import defaultdict

class StandPerformanceReport(Report):
    """
    Report showing the performance of car stands, including:
    - Average days on stand
    - Total profit from sold cars
    - Current cars on stand and their average age
    - Stand turnover rate
    """
    template_path = "reports/stand-performance.html"
    parameter_rules = {
        "stand_ids": {
            "type": "list",
            "required": False,
            "default": None
        },
        "start_date": {
            "type": "date",
            "required": False,
            "default": None
        },
        "end_date": {
            "type": "date",
            "required": False,
            "default": None
        },
        "vehicle_make": {
            "type": "string",
            "required": False,
            "default": None
        },
        "vehicle_model": {
            "type": "string",
            "required": False,
            "default": None
        }
    }

    def __init__(self, stand_ids=None, start_date=None, end_date=None, vehicle_make=None, vehicle_model=None):
        super().__init__()
        self.stand_ids = stand_ids
        self.start_date = start_date
        self.end_date = end_date
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        
        # Get thresholds from settings
        self.stand_aging_threshold_days = Setting.get_setting('stand_aging_threshold_days', 180, 'int')
        
    def generate(self):
        # Get all stands
        stands_query = Stand.query.order_by(Stand.stand_name)
        
        # Filter stands if stand_ids provided
        if self.stand_ids and len(self.stand_ids) > 0:
            stands_query = stands_query.filter(Stand.stand_id.in_(self.stand_ids))
            
        stands = stands_query.all()
        
        # Get all car makes and models for filters
        car_makes = Car.query.with_entities(Car.vehicle_make).distinct().order_by(Car.vehicle_make).all()
        car_models = Car.query.with_entities(Car.vehicle_model).distinct().order_by(Car.vehicle_model).all()
        
        # Transform into lists
        vehicle_makes = [make[0] for make in car_makes]
        vehicle_models = [model[0] for model in car_models]
        
        # Group models by make for dynamic filtering
        models_by_make = {}
        for car in Car.query.all():
            if car.vehicle_make not in models_by_make:
                models_by_make[car.vehicle_make] = []
            if car.vehicle_model not in models_by_make[car.vehicle_make]:
                models_by_make[car.vehicle_make].append(car.vehicle_model)
        
        # Sort model lists
        for make in models_by_make:
            models_by_make[make].sort()
        
        # Prepare stand performance data
        stands_data = []
        total_profit = 0
        total_avg_days = 0
        total_cars_on_stand = 0
        total_cars_sold = 0
        
        for stand in stands:
            # Build base query for cars that have been on this stand
            cars_query = Car.query.filter(Car.stand_id == stand.stand_id)
            
            # Apply date filters if provided for sold cars
            sold_cars_query = cars_query.filter(Car.date_sold != None)
            if self.start_date:
                sold_cars_query = sold_cars_query.filter(or_(
                    Car.date_bought >= self.start_date,
                    Car.date_sold >= self.start_date
                ))
            if self.end_date:
                sold_cars_query = sold_cars_query.filter(or_(
                    Car.date_bought <= self.end_date,
                    Car.date_sold <= self.end_date
                ))
                
            # Apply make/model filters if provided
            if self.vehicle_make:
                cars_query = cars_query.filter(Car.vehicle_make == self.vehicle_make)
                sold_cars_query = sold_cars_query.filter(Car.vehicle_make == self.vehicle_make)
            if self.vehicle_model:
                cars_query = cars_query.filter(Car.vehicle_model == self.vehicle_model)
                sold_cars_query = sold_cars_query.filter(Car.vehicle_model == self.vehicle_model)
                
            # Get current cars on stand
            current_cars_query = cars_query.filter(Car.date_sold == None)
            current_cars = current_cars_query.all()
            current_car_count = len(current_cars)
            
            # Calculate current cars' average age on stand
            current_avg_age = 0
            if current_car_count > 0:
                total_days = sum((datetime.now().date() - car.date_added_to_stand).days 
                               for car in current_cars if car.date_added_to_stand)
                current_avg_age = total_days / current_car_count if total_days > 0 else 0
            
            # Get sold cars data
            sold_cars = sold_cars_query.all()
            sold_car_count = len(sold_cars)
            
            # Calculate average days on stand for sold cars
            avg_days_on_stand = 0
            if sold_car_count > 0:
                total_sold_days = sum((car.date_sold - car.date_added_to_stand).days 
                                    for car in sold_cars if car.date_added_to_stand and car.date_sold)
                avg_days_on_stand = total_sold_days / sold_car_count if total_sold_days > 0 else 0
            
            # Calculate total profit from sold cars
            stand_profit = 0
            for car in sold_cars:
                # Get the sale for this car
                if hasattr(car, 'sale') and car.sale:
                    stand_profit += car.sale.profit if hasattr(car.sale, 'profit') else 0
            
            # Calculate turnover rate
            # This is cars sold divided by average cars on stand
            turnover_rate = 0
            avg_cars_on_stand = (current_car_count + sold_car_count) / 2 if current_car_count + sold_car_count > 0 else 1
            turnover_rate = sold_car_count / avg_cars_on_stand if avg_cars_on_stand > 0 else 0
            
            # Create aging bands for current cars
            aging_bands = self._calculate_aging_bands(current_cars)
            
            # Add to stands data
            stand_data = {
                'stand_id': stand.stand_id,
                'stand_name': stand.stand_name,
                'location': stand.location,
                'capacity': stand.capacity,
                'current_cars': current_car_count,
                'current_avg_age': current_avg_age,
                'sold_cars': sold_car_count,
                'avg_days_on_stand': avg_days_on_stand,
                'total_profit': stand_profit,
                'turnover_rate': turnover_rate,
                'utilization': (current_car_count / stand.capacity * 100) if stand.capacity > 0 else 0,
                'aging_bands': aging_bands
            }
            
            stands_data.append(stand_data)
            total_profit += stand_profit
            total_avg_days += avg_days_on_stand * sold_car_count  # Weighted average
            total_cars_on_stand += current_car_count
            total_cars_sold += sold_car_count
        
        # Calculate overall averages
        overall_avg_days = total_avg_days / total_cars_sold if total_cars_sold > 0 else 0
        overall_turnover_rate = total_cars_sold / ((total_cars_on_stand + total_cars_sold) / 2) if (total_cars_on_stand + total_cars_sold) > 0 else 0
        
        # Prepare summary data
        summary = {
            'total_stands': len(stands_data),
            'total_cars_on_stand': total_cars_on_stand,
            'total_cars_sold': total_cars_sold,
            'overall_avg_days_on_stand': overall_avg_days,
            'total_profit': total_profit,
            'overall_turnover_rate': overall_turnover_rate
        }
        
        # Sort stands by performance (using profit as default)
        stands_data.sort(key=lambda x: x['total_profit'], reverse=True)
        
        # Prepare bar chart data for avg days on stand
        chart_data = {
            'labels': [stand['stand_name'] for stand in stands_data],
            'avg_days_datasets': [stand['avg_days_on_stand'] for stand in stands_data],
            'turnover_datasets': [stand['turnover_rate'] for stand in stands_data],
            'profit_datasets': [float(stand['total_profit']) for stand in stands_data]
        }
        
        # If there are no stands with sales data, create test data to help debug the chart
        has_sales = any(stand['sold_cars'] > 0 for stand in stands_data) if stands_data else False
        
        if not has_sales:
            # Create a debug message first
            print("WARNING: No sales data found for any stand, but cars exist in the system.")
            print("Adding debug data to help troubleshoot chart rendering.")
            
            # For testing only - remove in production after fixing
            # Add a debug sample to see if the chart works at all
            if len(stands) > 0:
                # Add sample data points to help with debugging
                chart_data = {
                    'labels': ["Sample Stand 1", "Sample Stand 2"],
                    'avg_days_datasets': [15.5, 22.0],  
                    'turnover_datasets': [0.75, 0.5],
                    'profit_datasets': [15000.0, 8500.0]
                }
        
        # If no stands data at all, provide default empty chart data structure
        if not stands_data:
            chart_data = {
                'labels': [],
                'avg_days_datasets': [],
                'turnover_datasets': [],
                'profit_datasets': []
            }
            
            # Log a message about empty data
            print("Warning: No stand data found matching the current filters.")
        
        # Prepare the complete report data
        report_data = {
            'stands': stands_data,
            'summary': summary,
            'chart_data': chart_data,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'stand_aging_threshold_days': self.stand_aging_threshold_days,
            'stands_list': stands,
            'vehicle_makes': vehicle_makes,
            'vehicle_models': vehicle_models,
            'models_by_make': models_by_make,
            'stand_ids': self.stand_ids,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'vehicle_make': self.vehicle_make,
            'vehicle_model': self.vehicle_model
        }
        
        # Add a flag to indicate if there's actual stand data with sales
        has_stand_sales_data = any(stand['sold_cars'] > 0 for stand in stands_data) if stands_data else False
        report_data['has_stand_sales_data'] = has_stand_sales_data
        
        # Add a message if there's no data for the chart
        if not has_stand_sales_data:
            report_data['no_data_message'] = "No sales data found for the selected stands and filters. Try adjusting your filter criteria or adding sales data."
        
        return report_data
        
    def _calculate_aging_bands(self, cars):
        """Calculate aging bands for cars based on days on stand"""
        threshold = self.stand_aging_threshold_days
        bands = {
            'fresh': 0,  # 0-30 days
            'normal': 0,  # 31-60 days
            'aging': 0,   # 61-threshold days
            'critical': 0  # > threshold days
        }
        
        for car in cars:
            if not car.date_added_to_stand:
                continue
                
            days_on_stand = (datetime.now().date() - car.date_added_to_stand).days
            
            if days_on_stand <= 30:
                bands['fresh'] += 1
            elif days_on_stand <= 60:
                bands['normal'] += 1
            elif days_on_stand <= threshold:
                bands['aging'] += 1
            else:
                bands['critical'] += 1
                
        return bands 