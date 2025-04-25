from app.reports.base.report import Report
from app.models.repair import Repair
from app.models.car import Car
from app.models.repair_provider import RepairProvider
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from app.utils import import_helpers
import pandas as pd
import decimal
import calendar
import io

class RepairHistoryReport(Report):
    """
    Report analyzing repair costs and history, including metrics like:
    - Average cost per repair type
    - Average duration from purchase to first repair
    - Repair count per car
    - Average duration per provider
    
    With filtering options for repair type, provider, model/year and time range.
    """
    template_path = "reports/repair-history.html"
    
    # Parameter validation rules
    param_rules = {
        "start_date": (date, False, None),
        "end_date": (date, False, None),
        "repair_type": (str, False, None),
        "provider_id": (int, False, None),
        "vehicle_make": (str, False, None),
        "vehicle_model": (str, False, None),
        "year": (int, False, None)
    }
    
    def __init__(self, start_date=None, end_date=None, repair_type=None, 
                 provider_id=None, vehicle_make=None, vehicle_model=None, year=None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.repair_type = repair_type
        self.provider_id = provider_id
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        self.year = year
        self.months = [calendar.month_name[i] for i in range(1, 13)]
        
    def generate(self):
        """Generate the report data"""
        # Base query for repairs
        base_query = Repair.query.join(Repair.car)
        
        # Apply filters
        if self.start_date:
            base_query = base_query.filter(Repair.start_date >= self.start_date)
        
        if self.end_date:
            base_query = base_query.filter(Repair.start_date <= self.end_date)
            
        if self.repair_type:
            base_query = base_query.filter(Repair.repair_type == self.repair_type)
            
        if self.provider_id:
            base_query = base_query.filter(Repair.provider_id == self.provider_id)
            
        if self.vehicle_make:
            base_query = base_query.filter(Car.vehicle_make == self.vehicle_make)
            
        if self.vehicle_model:
            base_query = base_query.filter(Car.vehicle_model == self.vehicle_model)
            
        if self.year:
            base_query = base_query.filter(Car.year == self.year)
        
        # Get all repairs matching the filters
        repairs = base_query.all()
        
        # Calculate metrics
        avg_cost_per_type = self._calculate_avg_cost_per_type(repairs)
        avg_duration_from_purchase = self._calculate_avg_duration_from_purchase(repairs)
        repair_count_per_car = self._calculate_repair_count_per_car(repairs)
        avg_duration_per_provider = self._calculate_avg_duration_per_provider(repairs)
        cost_trend_per_type = self._calculate_cost_trend_per_type(repairs)
        repairs_by_model = self._group_repairs_by_car_model(repairs)
        
        # Get all available options for filtering
        available_repair_types = self._get_available_repair_types()
        available_providers = self._get_available_providers()
        available_makes = self._get_available_makes()
        available_models = self._get_available_models()
        available_years = self._get_available_years()
        
        # Return data for rendering
        self.data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "repair_type": self.repair_type,
            "provider_id": self.provider_id,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "year": self.year,
            
            # Metrics
            "avg_cost_per_type": avg_cost_per_type,
            "avg_duration_from_purchase": avg_duration_from_purchase,
            "repair_count_per_car": repair_count_per_car,
            "avg_duration_per_provider": avg_duration_per_provider,
            "cost_trend_per_type": cost_trend_per_type,
            "repairs_by_model": repairs_by_model,
            
            # Filter options
            "available_repair_types": available_repair_types,
            "available_providers": available_providers,
            "available_makes": available_makes,
            "available_models": available_models,
            "available_years": available_years,
            
            # For XLSX export
            "has_filters_applied": any([self.start_date, self.end_date, self.repair_type, 
                                      self.provider_id, self.vehicle_make, self.vehicle_model, self.year]),
            
            # Tooltips
            "tooltips": {
                "avg_cost": "Average cost for each repair type",
                "first_repair": "Average days between purchase and first repair",
                "repair_count": "Number of repairs per car",
                "duration": "Average repair duration by provider in days"
            }
        }
        
        return self.data
    
    def _calculate_avg_cost_per_type(self, repairs):
        """Calculate average cost per repair type"""
        repair_types = {}
        
        for repair in repairs:
            repair_type = repair.repair_type
            cost = self._to_decimal(repair.repair_cost)
            
            if repair_type not in repair_types:
                repair_types[repair_type] = {
                    "type": repair_type,
                    "count": 0,
                    "total_cost": decimal.Decimal('0.00')
                }
                
            repair_types[repair_type]["count"] += 1
            repair_types[repair_type]["total_cost"] += cost
            
        # Calculate average costs
        for repair_type in repair_types.values():
            repair_type["average_cost"] = repair_type["total_cost"] / repair_type["count"] if repair_type["count"] > 0 else 0
            
        # Sort by average cost descending
        return sorted(
            repair_types.values(),
            key=lambda x: x["average_cost"],
            reverse=True
        )
    
    def _calculate_avg_duration_from_purchase(self, repairs):
        """Calculate average days from purchase to first repair for each car"""
        car_first_repairs = {}
        
        # Get first repair for each car
        for repair in repairs:
            car_id = repair.car_id
            
            # Skip if we've already processed this car or missing purchase date
            if car_id in car_first_repairs or not repair.car.date_bought:
                continue
                
            # Calculate days from purchase to repair start
            days_to_first_repair = (repair.start_date - repair.car.date_bought).days
            
            car_first_repairs[car_id] = {
                "car_id": car_id,
                "car_name": f"{repair.car.year} {repair.car.vehicle_make} {repair.car.vehicle_model}",
                "purchase_date": repair.car.date_bought,
                "first_repair_date": repair.start_date,
                "days_to_repair": days_to_first_repair
            }
        
        # Calculate average
        avg_days = sum(item["days_to_repair"] for item in car_first_repairs.values()) / len(car_first_repairs) if car_first_repairs else 0
        
        return {
            "average_days": round(avg_days, 1),
            "cars": sorted(car_first_repairs.values(), key=lambda x: x["days_to_repair"], reverse=True)
        }
    
    def _calculate_repair_count_per_car(self, repairs):
        """Calculate repair count per car"""
        car_repairs = {}
        
        for repair in repairs:
            car_id = repair.car_id
            car = repair.car
            
            if car_id not in car_repairs:
                car_repairs[car_id] = {
                    "car_id": car_id,
                    "car_name": f"{car.year} {car.vehicle_make} {car.vehicle_model}",
                    "licence_number": car.licence_number,
                    "repairs": 0,
                    "total_cost": decimal.Decimal('0.00')
                }
                
            car_repairs[car_id]["repairs"] += 1
            car_repairs[car_id]["total_cost"] += self._to_decimal(repair.repair_cost)
        
        # Sort by repair count descending
        return sorted(car_repairs.values(), key=lambda x: x["repairs"], reverse=True)
    
    def _calculate_avg_duration_per_provider(self, repairs):
        """Calculate average repair duration per provider"""
        providers = {}
        
        for repair in repairs:
            if repair.duration is None:
                continue
                
            provider_id = repair.provider_id
            provider = repair.provider
            
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_id": provider_id,
                    "provider_name": provider.provider_name,
                    "service_type": provider.service_type,
                    "total_duration": 0,
                    "count": 0
                }
                
            providers[provider_id]["total_duration"] += repair.duration
            providers[provider_id]["count"] += 1
        
        # Calculate average duration
        for provider in providers.values():
            provider["average_duration"] = round(provider["total_duration"] / provider["count"], 1) if provider["count"] > 0 else 0
            
        # Sort by average duration ascending (fastest providers first)
        return sorted(providers.values(), key=lambda x: x["average_duration"])
    
    def _calculate_cost_trend_per_type(self, repairs):
        """Calculate cost trend per repair type over time (monthly)"""
        # If no date range is set, use full year of current or specified year
        year_to_use = self.year or datetime.now().year
        
        if not self.start_date and not self.end_date:
            start_date = date(year_to_use, 1, 1)
            end_date = date(year_to_use, 12, 31)
        else:
            start_date = self.start_date or min(repair.start_date for repair in repairs) if repairs else date.today()
            end_date = self.end_date or max(repair.start_date for repair in repairs) if repairs else date.today()
            
        # Get all unique repair types
        repair_types = set(repair.repair_type for repair in repairs)
        
        # Initialize data structure
        months_range = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            months_range.append(current_date.strftime("%Y-%m"))
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Initialize trend data
        trend_data = {
            "labels": [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months_range],
            "datasets": []
        }
        
        # Background colors for chart
        bg_colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69', '#858796']
        
        # Populate data for each repair type
        for idx, repair_type in enumerate(repair_types):
            # Initialize monthly data
            monthly_data = {month: {"count": 0, "total": 0} for month in months_range}
            
            # Populate with actual data
            for repair in repairs:
                if repair.repair_type == repair_type:
                    repair_month = repair.start_date.strftime("%Y-%m")
                    if repair_month in monthly_data:
                        monthly_data[repair_month]["count"] += 1
                        monthly_data[repair_month]["total"] += float(repair.repair_cost)
            
            # Calculate averages
            dataset = {
                "label": repair_type,
                "data": [
                    round(monthly_data[month]["total"] / monthly_data[month]["count"], 2) 
                    if monthly_data[month]["count"] > 0 else 0 
                    for month in months_range
                ],
                "backgroundColor": bg_colors[idx % len(bg_colors)]
            }
            
            trend_data["datasets"].append(dataset)
        
        return trend_data
    
    def _group_repairs_by_car_model(self, repairs):
        """Group repairs by car model/make/year"""
        model_repairs = {}
        
        for repair in repairs:
            car = repair.car
            model_key = f"{car.vehicle_make}-{car.vehicle_model}-{car.year}"
            
            if model_key not in model_repairs:
                model_repairs[model_key] = {
                    "make": car.vehicle_make,
                    "model": car.vehicle_model,
                    "year": car.year,
                    "full_name": f"{car.year} {car.vehicle_make} {car.vehicle_model}",
                    "repair_count": 0,
                    "total_cost": decimal.Decimal('0.00'),
                    "cars": set(),
                    "repair_types": {}
                }
                
            model_repairs[model_key]["repair_count"] += 1
            model_repairs[model_key]["total_cost"] += self._to_decimal(repair.repair_cost)
            model_repairs[model_key]["cars"].add(car.car_id)
            
            # Count repairs by type
            repair_type = repair.repair_type
            if repair_type not in model_repairs[model_key]["repair_types"]:
                model_repairs[model_key]["repair_types"][repair_type] = 0
            model_repairs[model_key]["repair_types"][repair_type] += 1
            
        # Convert car count and format data
        for model_data in model_repairs.values():
            model_data["car_count"] = len(model_data["cars"])
            model_data["cars"] = list(model_data["cars"])
            model_data["avg_cost_per_car"] = model_data["total_cost"] / model_data["car_count"] if model_data["car_count"] > 0 else 0
            model_data["common_repair"] = max(model_data["repair_types"].items(), key=lambda x: x[1])[0] if model_data["repair_types"] else "N/A"
            
        # Sort by repair count descending
        return sorted(model_repairs.values(), key=lambda x: x["repair_count"], reverse=True)
    
    def _get_available_repair_types(self):
        """Get all available repair types for filtering"""
        repair_types = Repair.query.with_entities(Repair.repair_type).distinct().all()
        return [r[0] for r in repair_types]
    
    def _get_available_providers(self):
        """Get all available providers for filtering"""
        return RepairProvider.query.all()
    
    def _get_available_makes(self):
        """Get all available vehicle makes for filtering"""
        makes = Car.query.with_entities(Car.vehicle_make).distinct().all()
        return [m[0] for m in makes]
    
    def _get_available_models(self):
        """Get all available vehicle models for filtering"""
        models = Car.query.with_entities(Car.vehicle_model).distinct().all()
        return [m[0] for m in models]
    
    def _get_available_years(self):
        """Get all available vehicle years for filtering"""
        years = Car.query.with_entities(Car.year).distinct().all()
        return sorted([y[0] for y in years], reverse=True)
    
    def _to_decimal(self, value):
        """Convert a value to Decimal safely"""
        if isinstance(value, decimal.Decimal):
            return value
        return decimal.Decimal(str(value)) if value is not None else decimal.Decimal('0.00')
        
    def export_xlsx(self):
        """Export report data to XLSX format"""
        # Generate report data if not already generated
        if not hasattr(self, 'data') or not self.data:
            self.generate()
            
        # Create Excel file
        output = io.BytesIO()
        
        # Create a Pandas Excel writer using XlsxWriter as the engine
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # Convert data to DataFrames and write to Excel
        
        # Sheet 1: Average Cost Per Repair Type
        if self.data['avg_cost_per_type']:
            df_cost = pd.DataFrame(self.data['avg_cost_per_type'])
            df_cost = df_cost[['type', 'count', 'total_cost', 'average_cost']]
            df_cost.columns = ['Repair Type', 'Count', 'Total Cost', 'Average Cost']
            df_cost.to_excel(writer, sheet_name='Avg Cost by Type', index=False)
        
        # Sheet 2: Repairs By Car Model
        if self.data['repairs_by_model']:
            model_data = []
            for model in self.data['repairs_by_model']:
                model_data.append({
                    'Make': model['make'],
                    'Model': model['model'],
                    'Year': model['year'],
                    'Repair Count': model['repair_count'],
                    'Total Cost': float(model['total_cost']),
                    'Car Count': model['car_count'],
                    'Avg Cost Per Car': float(model['avg_cost_per_car']),
                    'Most Common Repair': model['common_repair']
                })
            df_models = pd.DataFrame(model_data)
            df_models.to_excel(writer, sheet_name='Repairs By Model', index=False)
        
        # Sheet 3: Repair Count Per Car
        if self.data['repair_count_per_car']:
            df_cars = pd.DataFrame(self.data['repair_count_per_car'])
            df_cars = df_cars[['car_name', 'licence_number', 'repairs', 'total_cost']]
            df_cars.columns = ['Car', 'License Number', 'Repair Count', 'Total Cost']
            df_cars.to_excel(writer, sheet_name='Repairs Per Car', index=False)
        
        # Sheet 4: Avg Duration Per Provider
        if self.data['avg_duration_per_provider']:
            df_duration = pd.DataFrame(self.data['avg_duration_per_provider'])
            df_duration = df_duration[['provider_name', 'service_type', 'count', 'average_duration']]
            df_duration.columns = ['Provider', 'Service Type', 'Repair Count', 'Avg Duration (days)']
            df_duration.to_excel(writer, sheet_name='Duration By Provider', index=False)
        
        # Sheet 5: Avg Days to First Repair
        if self.data['avg_duration_from_purchase'] and self.data['avg_duration_from_purchase']['cars']:
            df_first = pd.DataFrame(self.data['avg_duration_from_purchase']['cars'])
            df_first = df_first[['car_name', 'purchase_date', 'first_repair_date', 'days_to_repair']]
            df_first.columns = ['Car', 'Purchase Date', 'First Repair Date', 'Days to First Repair']
            df_first.to_excel(writer, sheet_name='Days to First Repair', index=False)
        
        # Add report metadata
        metadata = {
            'Report': 'Repair Cost & History Analysis',
            'Generated On': self.data['report_date'],
            'Filters Applied': 'Yes' if self.data['has_filters_applied'] else 'No',
            'Start Date': self.data['start_date'] or 'All',
            'End Date': self.data['end_date'] or 'All',
            'Repair Type': self.data['repair_type'] or 'All',
            'Provider': self.data['provider_id'] or 'All',
            'Vehicle Make': self.data['vehicle_make'] or 'All',
            'Vehicle Model': self.data['vehicle_model'] or 'All',
            'Year': self.data['year'] or 'All'
        }
        
        pd.DataFrame([metadata]).to_excel(writer, sheet_name='Report Info', index=False)
        
        # Close the Pandas Excel writer and output the Excel file
        writer.close()
        output.seek(0)
        
        return output.getvalue() 