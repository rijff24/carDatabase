from app.reports.base.report import Report
from app.models.car import Car
from sqlalchemy import extract, func
from datetime import datetime

class InventoryAgingReport(Report):
    """
    Inventory Aging Report - Shows aging of current inventory, categorizing
    cars based on how long they've been in stock with investment tracking.
    """
    
    template_path = 'reports/inventory-aging.html'
    
    param_rules = {
        'status': (str, False, 'all')
    }
    
    def __init__(self):
        super().__init__()
        self.data = {}
    
    def generate(self):
        """Generate the inventory aging report data"""
        # Extract validated parameters
        status = self.params['status']
        
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
        self._calculate_days_in_inventory(inventory_cars)
        
        # Calculate average days in inventory
        total_days = sum(car.days_in_inventory for car in inventory_cars)
        avg_days_in_inventory = total_days / total_inventory if total_inventory else 0
        
        # Define and populate aging buckets
        aging_buckets = self._get_aging_buckets(inventory_cars, total_inventory)
        
        # Count aged vehicles (> 45 days)
        aged_vehicle_count = sum(
            bucket['count'] for bucket in aging_buckets 
            if bucket['min'] >= 46
        )
        aged_vehicle_percentage = (aged_vehicle_count / total_inventory * 100) if total_inventory else 0
        
        # Count cars by status
        status_counts = self._get_status_counts(inventory_cars)
        
        # Update data dictionary
        self.data.update({
            'total_inventory': total_inventory,
            'avg_days_in_inventory': avg_days_in_inventory,
            'total_investment': total_investment,
            'avg_investment_per_vehicle': avg_investment_per_vehicle,
            'aged_vehicle_count': aged_vehicle_count,
            'aged_vehicle_percentage': aged_vehicle_percentage,
            'aging_buckets': aging_buckets,
            'status_counts': status_counts,
            'cars': inventory_cars
        })
    
    def _calculate_days_in_inventory(self, cars):
        """Calculate days in inventory for each car"""
        for car in cars:
            if not hasattr(car, 'days_in_inventory') or not car.days_in_inventory:
                purchase_date = car.purchase_date
                today = datetime.now().date()
                delta = today - purchase_date
                car.days_in_inventory = delta.days
    
    def _get_aging_buckets(self, inventory_cars, total_inventory):
        """Define and populate aging buckets for inventory"""
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
        
        return aging_buckets
    
    def _get_status_counts(self, inventory_cars):
        """Count cars by status"""
        status_counts = {
            'reconditioning': len([car for car in inventory_cars if car.status == 'reconditioning']),
            'ready': len([car for car in inventory_cars if car.status == 'ready']),
            'stand': len([car for car in inventory_cars if car.status == 'stand'])
        }
        
        return status_counts 