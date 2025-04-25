from app.reports.base.report import Report
from app.models.part import Part, RepairPart
from app.models.repair import Repair
from app.models.car import Car
from app import db
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from app.utils import import_helpers
import pandas as pd
import decimal
import calendar
import io
import json

class PartsUsageReport(Report):
    """
    Report analyzing parts usage, including metrics like:
    - Most used parts
    - Average unit cost per part over time
    - Parts most used per vehicle model
    - Top 10 parts by frequency
    
    With filtering options for time range, part name, and vehicle model.
    """
    template_path = "reports/parts-usage.html"
    
    # Parameter validation rules
    param_rules = {
        "start_date": (date, False, None),
        "end_date": (date, False, None),
        "part_name": (str, False, None),
        "vehicle_model": (str, False, None)
    }
    
    def __init__(self, start_date=None, end_date=None, part_name=None, vehicle_model=None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.part_name = part_name
        self.vehicle_model = vehicle_model
        self.months = [calendar.month_name[i] for i in range(1, 13)]
        
    def generate(self):
        """Generate the report data"""
        # Base query for repair parts
        base_query = db.session.query(
            RepairPart, Repair, Part, Car
        ).join(
            Repair, RepairPart.repair_id == Repair.repair_id
        ).join(
            Part, RepairPart.part_id == Part.part_id
        ).join(
            Car, Repair.car_id == Car.car_id
        )
        
        # Apply filters
        if self.start_date:
            base_query = base_query.filter(RepairPart.purchase_date >= self.start_date)
        
        if self.end_date:
            base_query = base_query.filter(RepairPart.purchase_date <= self.end_date)
            
        if self.part_name:
            base_query = base_query.filter(Part.part_name.ilike(f'%{self.part_name}%'))
            
        if self.vehicle_model:
            base_query = base_query.filter(Car.vehicle_model == self.vehicle_model)
        
        # Get all repair parts data
        repair_parts_data = base_query.all()
        
        # Calculate metrics
        most_used_parts = self._calculate_most_used_parts(repair_parts_data)
        avg_unit_cost_over_time = self._calculate_avg_unit_cost_over_time(repair_parts_data)
        parts_most_used_per_model = self._calculate_parts_most_used_per_model(repair_parts_data)
        top_parts_by_frequency = self._get_top_parts_by_frequency(repair_parts_data, limit=10)
        
        # Get all available options for filtering
        available_parts = self._get_available_parts()
        available_models = self._get_available_models()
        
        # Return data for rendering
        self.data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "part_name": self.part_name,
            "vehicle_model": self.vehicle_model,
            
            # Metrics
            "most_used_parts": most_used_parts,
            "avg_unit_cost_over_time": avg_unit_cost_over_time,
            "parts_most_used_per_model": parts_most_used_per_model,
            "top_parts_by_frequency": top_parts_by_frequency,
            
            # Filter options
            "available_parts": available_parts,
            "available_models": available_models,
            
            # For XLSX export
            "has_filters_applied": any([self.start_date, self.end_date, self.part_name, self.vehicle_model]),
            
            # Tooltips
            "tooltips": {
                "most_used": "Parts most frequently used in repairs",
                "unit_cost": "Average cost per part over time",
                "per_model": "Parts most commonly used for each vehicle model",
                "frequency": "Top 10 parts by frequency of use"
            }
        }
        
        return self.data
    
    def _calculate_most_used_parts(self, repair_parts_data):
        """Calculate most frequently used parts"""
        part_usage = {}
        
        for rp, repair, part, car in repair_parts_data:
            part_id = part.part_id
            
            if part_id not in part_usage:
                part_usage[part_id] = {
                    "part_id": part_id,
                    "part_name": part.part_name,
                    "manufacturer": part.manufacturer,
                    "count": 0,
                    "total_cost": decimal.Decimal('0.00'),
                    "repairs": set(),
                    "models": set()
                }
                
            part_usage[part_id]["count"] += 1
            part_usage[part_id]["total_cost"] += self._to_decimal(rp.purchase_price)
            part_usage[part_id]["repairs"].add(repair.repair_id)
            part_usage[part_id]["models"].add(car.vehicle_model)
            
        # Calculate average costs and format data
        for part_data in part_usage.values():
            part_data["avg_cost"] = part_data["total_cost"] / part_data["count"] if part_data["count"] > 0 else 0
            part_data["repairs"] = len(part_data["repairs"])
            part_data["models"] = len(part_data["models"])
            
        # Sort by count descending
        return sorted(part_usage.values(), key=lambda x: x["count"], reverse=True)
    
    def _calculate_avg_unit_cost_over_time(self, repair_parts_data):
        """Calculate average unit cost per part over time"""
        # If no date range is set, use last 12 months
        if not self.start_date and not self.end_date:
            end_date = date.today()
            start_date = date(end_date.year - 1, end_date.month, 1)
        else:
            start_date = self.start_date or min(rp.purchase_date for rp, _, _, _ in repair_parts_data) if repair_parts_data else date.today()
            end_date = self.end_date or max(rp.purchase_date for rp, _, _, _ in repair_parts_data) if repair_parts_data else date.today()
            
        # Get all unique parts
        parts = {part.part_id: part.part_name for _, _, part, _ in repair_parts_data}
        
        if not parts:
            return {"labels": [], "datasets": []}
        
        # Initialize data structure for months
        months_range = []
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            months_range.append(current_date.strftime("%Y-%m"))
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Initialize monthly data for each part
        part_monthly_data = {part_id: {month: {"count": 0, "total": 0} for month in months_range} for part_id in parts}
        
        # Populate with actual data
        for rp, _, part, _ in repair_parts_data:
            purchase_month = rp.purchase_date.strftime("%Y-%m")
            if purchase_month in months_range and part.part_id in part_monthly_data:
                part_monthly_data[part.part_id][purchase_month]["count"] += 1
                part_monthly_data[part.part_id][purchase_month]["total"] += float(rp.purchase_price)
        
        # Initialize trend data
        trend_data = {
            "labels": [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months_range],
            "datasets": []
        }
        
        # Background colors for chart
        bg_colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#5a5c69', '#858796']
        
        # Get top 5 most used parts for the chart
        top_parts = sorted(parts.items(), key=lambda x: sum(data[month]["count"] for month in months_range 
                                                for part_id, data in part_monthly_data.items() 
                                                if part_id == x[0]), reverse=True)[:5]
        
        # Populate datasets for each part
        for idx, (part_id, part_name) in enumerate(top_parts):
            # Calculate monthly averages
            data = [
                round(part_monthly_data[part_id][month]["total"] / part_monthly_data[part_id][month]["count"], 2)
                if part_monthly_data[part_id][month]["count"] > 0 else None
                for month in months_range
            ]
            
            dataset = {
                "label": part_name,
                "data": data,
                "backgroundColor": bg_colors[idx % len(bg_colors)],
                "borderColor": bg_colors[idx % len(bg_colors)],
                "borderWidth": 2,
                "fill": False
            }
            
            trend_data["datasets"].append(dataset)
        
        return trend_data
    
    def _calculate_parts_most_used_per_model(self, repair_parts_data):
        """Calculate parts most frequently used for each vehicle model"""
        model_parts = {}
        
        for rp, repair, part, car in repair_parts_data:
            model = car.vehicle_model
            
            if model not in model_parts:
                model_parts[model] = {
                    "model": model,
                    "make": car.vehicle_make,
                    "part_usage": {}
                }
                
            if part.part_id not in model_parts[model]["part_usage"]:
                model_parts[model]["part_usage"][part.part_id] = {
                    "part_name": part.part_name,
                    "count": 0,
                    "total_cost": decimal.Decimal('0.00')
                }
                
            model_parts[model]["part_usage"][part.part_id]["count"] += 1
            model_parts[model]["part_usage"][part.part_id]["total_cost"] += self._to_decimal(rp.purchase_price)
        
        # Sort parts by usage and limit to top 5 for each model
        for model_data in model_parts.values():
            top_parts = sorted(model_data["part_usage"].values(), key=lambda x: x["count"], reverse=True)[:5]
            model_data["top_parts"] = top_parts
            model_data["total_parts_used"] = sum(part["count"] for part in model_data["part_usage"].values())
            del model_data["part_usage"]  # Remove raw data to keep response size reasonable
            
        # Sort models by total parts used
        return sorted(model_parts.values(), key=lambda x: x["total_parts_used"], reverse=True)
    
    def _get_top_parts_by_frequency(self, repair_parts_data, limit=10):
        """Get top N parts by frequency of use"""
        part_frequency = {}
        
        for rp, repair, part, car in repair_parts_data:
            part_id = part.part_id
            
            if part_id not in part_frequency:
                part_frequency[part_id] = {
                    "part_id": part_id,
                    "part_name": part.part_name,
                    "manufacturer": part.manufacturer,
                    "count": 0,
                    "models": set()
                }
                
            part_frequency[part_id]["count"] += 1
            part_frequency[part_id]["models"].add(f"{car.vehicle_make} {car.vehicle_model}")
        
        # Format data
        for part_data in part_frequency.values():
            part_data["models"] = list(part_data["models"])
            part_data["model_count"] = len(part_data["models"])
            part_data["most_common_models"] = ", ".join(part_data["models"][:3])
            if len(part_data["models"]) > 3:
                part_data["most_common_models"] += f" and {len(part_data['models']) - 3} more"
            del part_data["models"]  # Remove raw data
            
        # Get top N by frequency
        return sorted(part_frequency.values(), key=lambda x: x["count"], reverse=True)[:limit]
    
    def _get_available_parts(self):
        """Get all available parts for filtering"""
        parts = Part.query.order_by(Part.part_name).all()
        return parts
    
    def _get_available_models(self):
        """Get all available vehicle models for filtering"""
        models = Car.query.with_entities(Car.vehicle_model).distinct().order_by(Car.vehicle_model).all()
        return [m[0] for m in models]
    
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
        
        # Sheet 1: Most Used Parts
        if self.data['most_used_parts']:
            df_most_used = pd.DataFrame(self.data['most_used_parts'])
            df_most_used = df_most_used[['part_name', 'manufacturer', 'count', 'avg_cost', 'repairs', 'models']]
            df_most_used.columns = ['Part Name', 'Manufacturer', 'Usage Count', 'Avg Cost ($)', 'Repairs Used In', 'Models Used On']
            df_most_used.to_excel(writer, sheet_name='Most Used Parts', index=False)
        
        # Sheet 2: Top Parts by Frequency
        if self.data['top_parts_by_frequency']:
            df_top = pd.DataFrame(self.data['top_parts_by_frequency'])
            df_top = df_top[['part_name', 'manufacturer', 'count', 'model_count', 'most_common_models']]
            df_top.columns = ['Part Name', 'Manufacturer', 'Frequency', 'Model Count', 'Most Common Models']
            df_top.to_excel(writer, sheet_name='Top Parts by Frequency', index=False)
        
        # Sheet 3: Parts by Model
        if self.data['parts_most_used_per_model']:
            model_data = []
            for model in self.data['parts_most_used_per_model']:
                for idx, part in enumerate(model['top_parts']):
                    model_data.append({
                        'Model': model['model'],
                        'Make': model['make'],
                        'Part Name': part['part_name'],
                        'Usage Count': part['count'],
                        'Total Cost': float(part['total_cost']),
                        'Rank': idx + 1
                    })
            df_model = pd.DataFrame(model_data)
            df_model.to_excel(writer, sheet_name='Parts by Model', index=False)
        
        # Add report metadata
        metadata = {
            'Report': 'Parts Usage Analysis',
            'Generated On': self.data['report_date'],
            'Filters Applied': 'Yes' if self.data['has_filters_applied'] else 'No',
            'Start Date': self.data['start_date'] or 'All',
            'End Date': self.data['end_date'] or 'All',
            'Part Name': self.data['part_name'] or 'All',
            'Vehicle Model': self.data['vehicle_model'] or 'All'
        }
        
        pd.DataFrame([metadata]).to_excel(writer, sheet_name='Report Info', index=False)
        
        # Close the Pandas Excel writer and output the Excel file
        writer.close()
        output.seek(0)
        
        return output.getvalue() 