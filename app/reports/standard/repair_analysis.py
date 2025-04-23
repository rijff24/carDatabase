from app.reports.base import Report
from app.models import Repair, RepairProvider, Car
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
import decimal
import calendar

class RepairAnalysisReport(Report):
    """
    Report showing repair costs by type and provider, repair duration,
    and monthly repair cost trends.
    """
    template_path = "reports/repair-analysis.html"
    parameter_rules = {
        "year": {
            "type": "integer",
            "required": False,
            "default": datetime.now().year
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
        "provider_id": {
            "type": "integer",
            "required": False,
            "default": None
        },
        "repair_type": {
            "type": "string",
            "required": False,
            "default": None
        }
    }

    def __init__(self, year=None, start_date=None, end_date=None, provider_id=None, repair_type=None):
        super().__init__()
        self.year = year or self.parameter_rules["year"]["default"]
        self.start_date = start_date
        self.end_date = end_date
        self.provider_id = provider_id
        self.repair_type = repair_type
        self.months = [calendar.month_name[i] for i in range(1, 13)]
        
    def generate(self):
        # Base query for repairs
        base_query = Repair.query
        
        # Apply filters
        if self.start_date and self.end_date:
            base_query = base_query.filter(Repair.start_date >= self.start_date, Repair.start_date <= self.end_date)
        elif self.year:
            base_query = base_query.filter(extract('year', Repair.start_date) == self.year)
            
        if self.provider_id:
            base_query = base_query.filter(Repair.provider_id == self.provider_id)
            
        if self.repair_type:
            base_query = base_query.filter(Repair.repair_type == self.repair_type)
        
        # Get all repairs matching the filters
        repairs = base_query.all()
        
        # Calculate total metrics
        total_repairs = len(repairs)
        total_cost = sum(self._decimal(repair.repair_cost) for repair in repairs)
        average_cost = total_cost / total_repairs if total_repairs > 0 else decimal.Decimal('0.00')
        
        # Calculate average repair duration
        durations = [repair.duration for repair in repairs if repair.duration is not None]
        average_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate repair costs by type
        repair_costs_by_type = self._get_repair_costs_by_type(repairs)
        
        # Calculate repair costs by provider
        repair_costs_by_provider = self._get_repair_costs_by_provider(repairs)
        
        # Calculate average repair duration by type
        repair_duration_by_type = self._get_repair_duration_by_type(repairs)
        
        # Calculate average repair duration by provider
        repair_duration_by_provider = self._get_repair_duration_by_provider(repairs)
        
        # Calculate monthly costs
        monthly_costs = self._get_monthly_costs(self.year, self.start_date, self.end_date)
        
        # Calculate maximum average duration for UI rendering
        max_duration = max([data["average_duration"] for data in repair_duration_by_type]) if repair_duration_by_type else 0
        
        # Get all available repair types for filtering
        repair_types = Repair.query.with_entities(Repair.repair_type).distinct().all()
        repair_types = [r[0] for r in repair_types]
        
        # Get all available providers for filtering
        providers = RepairProvider.query.all()
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "year": self.year,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "provider_id": self.provider_id,
            "repair_type": self.repair_type,
            "total_repairs": total_repairs,
            "total_cost": total_cost,
            "average_cost": average_cost,
            "average_duration": average_duration,
            "repair_costs_by_type": repair_costs_by_type,
            "repairs_by_type": repair_costs_by_type,  # For template compatibility
            "repair_costs_by_provider": repair_costs_by_provider,
            "repairs_by_provider": repair_costs_by_provider,  # For template compatibility
            "repair_duration_by_type": repair_duration_by_type,
            "repair_duration_by_provider": repair_duration_by_provider,
            "monthly_costs": monthly_costs,
            "max_duration": max_duration,
            "available_repair_types": repair_types,
            "available_providers": providers,
            "tooltips": {
                "average_duration": "The average number of days from repair start to completion",
                "repair_type": "Category of repair (mechanical, electrical, etc.)",
                "provider": "The vendor or shop that performed the repair"
            }
        }
    
    def _decimal(self, value):
        """Convert a value to Decimal safely"""
        if isinstance(value, decimal.Decimal):
            return value
        return decimal.Decimal(str(value)) if value is not None else decimal.Decimal('0.00')
    
    def _get_repair_costs_by_type(self, repairs):
        """Calculate repair costs grouped by type"""
        repair_types = {}
        
        for repair in repairs:
            repair_type = repair.repair_type
            cost = self._decimal(repair.repair_cost)
            
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
            repair_type["average_cost"] = repair_type["total_cost"] / repair_type["count"]
            
        # Sort by total cost descending
        return sorted(
            repair_types.values(),
            key=lambda x: x["total_cost"],
            reverse=True
        )
    
    def _get_repair_costs_by_provider(self, repairs):
        """Calculate repair costs grouped by provider"""
        providers = {}
        
        for repair in repairs:
            provider_id = repair.provider_id
            provider = RepairProvider.query.get(provider_id)
            
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_id": provider_id,
                    "provider_name": provider.provider_name if provider else "Unknown",
                    "name": provider.provider_name if provider else "Unknown",  # For template compatibility
                    "count": 0,
                    "total_cost": decimal.Decimal('0.00')
                }
                
            providers[provider_id]["count"] += 1
            providers[provider_id]["total_cost"] += self._decimal(repair.repair_cost)
            
        # Calculate average cost
        for provider in providers.values():
            provider["average_cost"] = provider["total_cost"] / provider["count"] if provider["count"] > 0 else 0
            
        # Return as list sorted by count (descending)
        return sorted(
            providers.values(),
            key=lambda x: x["count"],
            reverse=True
        )
    
    def _get_repair_duration_by_type(self, repairs):
        """Compute average repair duration by type"""
        repair_types = {}
        
        for repair in repairs:
            if repair.duration is None:
                continue
                
            repair_type = repair.repair_type
            
            if repair_type not in repair_types:
                repair_types[repair_type] = {
                    "type": repair_type,
                    "total_duration": 0,
                    "count": 0
                }
                
            repair_types[repair_type]["total_duration"] += repair.duration
            repair_types[repair_type]["count"] += 1
            
        # Calculate average duration
        for repair_type in repair_types.values():
            repair_type["average_duration"] = repair_type["total_duration"] / repair_type["count"]
            
        # Sort by average duration descending
        return sorted(
            repair_types.values(),
            key=lambda x: x["average_duration"],
            reverse=True
        )
    
    def _get_repair_duration_by_provider(self, repairs):
        """Compute average repair duration by provider"""
        providers = {}
        
        for repair in repairs:
            if repair.duration is None:
                continue
                
            provider_id = repair.provider_id
            provider = RepairProvider.query.get(provider_id)
            
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_id": provider_id,
                    "provider_name": provider.provider_name if provider else "Unknown",
                    "name": provider.provider_name if provider else "Unknown",  # For template compatibility
                    "total_duration": 0,
                    "count": 0
                }
                
            providers[provider_id]["total_duration"] += repair.duration
            providers[provider_id]["count"] += 1
            
        # Calculate average duration
        for provider in providers.values():
            provider["average_duration"] = provider["total_duration"] / provider["count"] if provider["count"] > 0 else 0
            
        # Sort by average duration (ascending is better)
        return sorted(
            providers.values(),
            key=lambda x: x["average_duration"]
        )
    
    def _get_monthly_costs(self, year=None, start_date=None, end_date=None):
        """Get repair costs by month for the specified period"""
        monthly_data = []
        
        # If specific date range is provided
        if start_date and end_date:
            # Create a list of month/year combinations in the date range
            current_date = start_date.replace(day=1)
            end_of_range = end_date.replace(day=1)
            
            while current_date <= end_of_range:
                current_month = current_date.month
                current_year = current_date.year
                
                # Query for repairs in this month/year
                month_repairs = Repair.query.filter(
                    extract('year', Repair.start_date) == current_year,
                    extract('month', Repair.start_date) == current_month
                )
                
                # Apply other filters if they exist
                if self.provider_id:
                    month_repairs = month_repairs.filter(Repair.provider_id == self.provider_id)
                if self.repair_type:
                    month_repairs = month_repairs.filter(Repair.repair_type == self.repair_type)
                    
                # Get all repairs for this month
                month_repairs = month_repairs.all()
                
                # Calculate totals for this month
                month_count = len(month_repairs)
                month_total_cost = sum(self._decimal(repair.repair_cost) for repair in month_repairs)
                month_average_cost = month_total_cost / month_count if month_count > 0 else decimal.Decimal('0.00')
                
                monthly_data.append({
                    "month": current_month,
                    "year": current_year,
                    "name": f"{calendar.month_name[current_month]} {current_year}",
                    "month_name": calendar.month_name[current_month],
                    "count": month_count,
                    "total_cost": month_total_cost,
                    "average_cost": month_average_cost
                })
                
                # Move to next month
                if current_month == 12:
                    current_date = current_date.replace(year=current_year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_month + 1)
        
        # If only year is specified
        elif year:
            for month in range(1, 13):
                # Query for repairs in this month/year
                month_repairs = Repair.query.filter(
                    extract('year', Repair.start_date) == year,
                    extract('month', Repair.start_date) == month
                )
                
                # Apply other filters if they exist
                if self.provider_id:
                    month_repairs = month_repairs.filter(Repair.provider_id == self.provider_id)
                if self.repair_type:
                    month_repairs = month_repairs.filter(Repair.repair_type == self.repair_type)
                    
                # Get all repairs for this month
                month_repairs = month_repairs.all()
                
                # Calculate totals for this month
                month_count = len(month_repairs)
                month_total_cost = sum(self._decimal(repair.repair_cost) for repair in month_repairs)
                month_average_cost = month_total_cost / month_count if month_count > 0 else decimal.Decimal('0.00')
                
                monthly_data.append({
                    "month": month,
                    "year": year,
                    "name": calendar.month_name[month],
                    "month_name": calendar.month_name[month],
                    "count": month_count,
                    "total_cost": month_total_cost,
                    "average_cost": month_average_cost
                })
            
        return monthly_data 