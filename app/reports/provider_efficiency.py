from app.reports.base.report import Report
from app.models.repair import Repair
from app.models.car import Car
from app.models.repair_provider import RepairProvider
from sqlalchemy import func, extract, desc, asc
from datetime import datetime, date, timedelta
from app.utils import import_helpers
import pandas as pd
import decimal
import calendar
import io
import os

class ProviderEfficiencyReport(Report):
    """
    Report tracking Repair Provider Performance, including metrics like:
    - Average repair cost per provider
    - Average duration per repair
    - Number of repairs handled
    
    With filtering options for repair type and date range.
    """
    template_path = "reports/provider-efficiency.html"
    
    # Parameter validation rules
    param_rules = {
        "start_date": (date, False, None),
        "end_date": (date, False, None),
        "repair_type": (str, False, None)
    }
    
    def __init__(self, start_date=None, end_date=None, repair_type=None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.repair_type = repair_type
        self.months = [calendar.month_name[i] for i in range(1, 13)]
        
    def generate(self):
        """Generate the report data"""
        # Base query for repairs
        base_query = Repair.query.join(Repair.provider)
        
        # Apply filters
        if self.start_date:
            base_query = base_query.filter(Repair.start_date >= self.start_date)
        
        if self.end_date:
            base_query = base_query.filter(Repair.start_date <= self.end_date)
            
        if self.repair_type:
            base_query = base_query.filter(Repair.repair_type == self.repair_type)
        
        # Get all repairs matching the filters
        repairs = base_query.all()
        
        # Calculate metrics
        provider_metrics = self._calculate_provider_metrics(repairs)
        cost_vs_duration = self._calculate_cost_vs_duration(repairs)
        available_repair_types = self._get_available_repair_types()
        
        # Return data for rendering
        self.data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "repair_type": self.repair_type,
            
            # Metrics
            "provider_metrics": provider_metrics,
            "cost_vs_duration": cost_vs_duration,
            
            # Filter options
            "available_repair_types": available_repair_types,
            
            # For XLSX export
            "has_filters_applied": any([self.start_date, self.end_date, self.repair_type]),
            
            # Tooltips
            "tooltips": {
                "avg_cost": "Average cost of repairs per provider",
                "avg_duration": "Average repair duration in days",
                "total_repairs": "Total number of repairs handled",
                "cost_duration_ratio": "Cost/duration ratio (lower is more efficient)"
            }
        }
        
        return self.data
    
    def _calculate_provider_metrics(self, repairs):
        """Calculate metrics for each provider"""
        providers = {}
        
        for repair in repairs:
            provider_id = repair.provider_id
            provider = repair.provider
            cost = self._to_decimal(repair.repair_cost)
            
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_id": provider_id,
                    "provider_name": provider.provider_name,
                    "service_type": provider.service_type,
                    "total_cost": decimal.Decimal('0.00'),
                    "total_repairs": 0,
                    "completed_repairs": 0,
                    "total_duration": 0
                }
                
            providers[provider_id]["total_cost"] += cost
            providers[provider_id]["total_repairs"] += 1
            
            # Calculate duration for completed repairs
            if repair.duration is not None:
                providers[provider_id]["completed_repairs"] += 1
                providers[provider_id]["total_duration"] += repair.duration
        
        # Calculate averages
        for provider in providers.values():
            provider["avg_cost"] = provider["total_cost"] / provider["total_repairs"] if provider["total_repairs"] > 0 else 0
            provider["avg_duration"] = provider["total_duration"] / provider["completed_repairs"] if provider["completed_repairs"] > 0 else 0
            
            # Calculate cost/duration efficiency ratio (lower is better)
            if provider["avg_duration"] > 0:
                provider["cost_duration_ratio"] = float(provider["avg_cost"]) / float(provider["avg_duration"])
            else:
                provider["cost_duration_ratio"] = None
        
        # Sort by average cost
        return sorted(
            providers.values(),
            key=lambda x: x["avg_cost"] if x["avg_cost"] is not None else float('inf')
        )
    
    def _calculate_cost_vs_duration(self, repairs):
        """Calculate cost vs duration comparison data for visualization"""
        providers = {}
        
        for repair in repairs:
            if repair.duration is None:
                continue
                
            provider_id = repair.provider_id
            provider = repair.provider
            cost = self._to_decimal(repair.repair_cost)
            
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_id": provider_id,
                    "provider_name": provider.provider_name,
                    "service_type": provider.service_type,
                    "avg_cost": 0,
                    "avg_duration": 0,
                    "total_cost": decimal.Decimal('0.00'),
                    "total_duration": 0,
                    "count": 0
                }
                
            providers[provider_id]["total_cost"] += cost
            providers[provider_id]["total_duration"] += repair.duration
            providers[provider_id]["count"] += 1
        
        # Calculate averages
        for provider in providers.values():
            provider["avg_cost"] = float(provider["total_cost"] / provider["count"]) if provider["count"] > 0 else 0
            provider["avg_duration"] = provider["total_duration"] / provider["count"] if provider["count"] > 0 else 0
        
        # Return data for chart visualization
        return sorted(providers.values(), key=lambda x: x["provider_name"])
    
    def _get_available_repair_types(self):
        """Get list of all available repair types for filtering"""
        repair_types = Repair.query.with_entities(Repair.repair_type).distinct().all()
        return [r[0] for r in repair_types]
    
    def _to_decimal(self, value):
        """Convert value to decimal, handling None values"""
        if value is None:
            return decimal.Decimal('0.00')
        return decimal.Decimal(str(value))
    
    def export_xlsx(self):
        """Export report data to Excel format"""
        # Generate report data if not already generated
        if not hasattr(self, 'data'):
            self.generate()
            
        # Create Excel file
        output = io.BytesIO()
        
        # Create a pandas ExcelWriter object
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Create DataFrame for provider metrics
            provider_df = pd.DataFrame([
                {
                    'Provider Name': p['provider_name'],
                    'Service Type': p['service_type'],
                    'Total Repairs': p['total_repairs'],
                    'Average Cost': float(p['avg_cost']),
                    'Average Duration (days)': float(p['avg_duration']) if p['avg_duration'] is not None else 0,
                    'Cost/Duration Ratio': float(p['cost_duration_ratio']) if p['cost_duration_ratio'] is not None else 0
                }
                for p in self.data['provider_metrics']
            ])
            
            # Write to Excel with formatting
            provider_df.to_excel(writer, sheet_name='Provider Metrics', index=False)
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Provider Metrics']
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '"$"#,##0.00'
            })
            
            # Apply formats
            for col_num, value in enumerate(provider_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set column widths
            worksheet.set_column('A:A', 25)  # Provider Name
            worksheet.set_column('B:B', 15)  # Service Type
            worksheet.set_column('C:C', 15)  # Total Repairs
            worksheet.set_column('D:D', 15)  # Average Cost
            worksheet.set_column('E:E', 20)  # Average Duration
            worksheet.set_column('F:F', 20)  # Cost/Duration Ratio
            
            # Format currency columns
            worksheet.set_column('D:D', 15, currency_format)
            
            # Add report filters
            filters_df = pd.DataFrame([
                {'Parameter': 'Report Date', 'Value': self.data['report_date']},
                {'Parameter': 'Start Date', 'Value': self.data['start_date'] if self.data['start_date'] else 'All Time'},
                {'Parameter': 'End Date', 'Value': self.data['end_date'] if self.data['end_date'] else 'Present'},
                {'Parameter': 'Repair Type', 'Value': self.data['repair_type'] if self.data['repair_type'] else 'All Types'}
            ])
            
            filters_df.to_excel(writer, sheet_name='Filters', index=False)
            filter_worksheet = writer.sheets['Filters']
            
            # Format filter sheet
            filter_worksheet.set_column('A:A', 20)
            filter_worksheet.set_column('B:B', 30)
            
            for col_num, value in enumerate(filters_df.columns.values):
                filter_worksheet.write(0, col_num, value, header_format)
            
        # Reset the pointer to the start
        output.seek(0)
        return output.getvalue() 