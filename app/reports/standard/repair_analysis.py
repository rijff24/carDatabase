from app.reports.base.report import Report
from app.models.repair import Repair
from app.models.repair_provider import RepairProvider
from sqlalchemy import extract, func
from datetime import datetime
from collections import defaultdict

class RepairAnalysisReport(Report):
    """
    Repair Cost Analysis Report - Shows repair costs by type and provider,
    repair duration, and monthly repair costs trends.
    """
    
    template_path = 'reports/repair-analysis.html'
    
    param_rules = {
        'year': (int, False, lambda: datetime.now().year)
    }
    
    def __init__(self):
        super().__init__()
        self.data = {
            'current_year': datetime.now().year,
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        }
    
    def generate(self):
        """Generate the repair analysis report data"""
        # Extract validated parameters
        year = self.params['year']
        
        # Query repairs within the specified year
        repairs = Repair.query.filter(
            extract('year', Repair.start_date) == year
        ).all()
        
        # Calculate total metrics
        total_repairs = len(repairs)
        total_cost = sum(float(repair.repair_cost) for repair in repairs)
        avg_cost_per_repair = total_cost / total_repairs if total_repairs else 0
        
        # Process repair data by type and provider
        repair_by_type = self._get_repair_costs_by_type(repairs)
        repair_by_provider = self._get_repair_costs_by_provider(repairs)
        repair_duration = self._get_repair_duration_by_type(repairs)
        costs = self._get_monthly_costs(repairs)
        
        # Update data dictionary with generated values
        self.data.update({
            'total_repairs': total_repairs,
            'total_cost': total_cost,
            'avg_cost_per_repair': avg_cost_per_repair,
            'repair_by_type': repair_by_type,
            'repair_by_provider': repair_by_provider,
            'repair_duration': repair_duration,
            'costs': costs
        })
    
    def _get_repair_costs_by_type(self, repairs):
        """Get repair costs grouped by repair type"""
        repair_types = {}
        for repair in repairs:
            if repair.repair_type not in repair_types:
                repair_types[repair.repair_type] = {
                    'count': 0, 
                    'total_cost': 0
                }
            repair_types[repair.repair_type]['count'] += 1
            repair_types[repair.repair_type]['total_cost'] += float(repair.repair_cost)
        
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
        
        return repair_by_type
    
    def _get_repair_costs_by_provider(self, repairs):
        """Get repair costs grouped by repair provider"""
        repair_providers = {}
        for repair in repairs:
            provider_id = repair.provider_id
            provider = RepairProvider.query.get(provider_id)
            provider_name = provider.provider_name if provider else 'Unknown'
            
            if provider_name not in repair_providers:
                repair_providers[provider_name] = {
                    'count': 0, 
                    'total_cost': 0
                }
            repair_providers[provider_name]['count'] += 1
            repair_providers[provider_name]['total_cost'] += float(repair.repair_cost)
        
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
        
        return repair_by_provider
    
    def _get_repair_duration_by_type(self, repairs):
        """Get average repair duration by repair type"""
        repair_types = {}
        for repair in repairs:
            if repair.repair_type not in repair_types:
                repair_types[repair.repair_type] = []
            repair_types[repair.repair_type].append(repair)
        
        repair_duration = []
        for rtype, type_repairs in repair_types.items():
            # Only include repairs with a duration (where end_date is set)
            repairs_with_duration = [r for r in type_repairs if r.duration is not None]
            if not repairs_with_duration:
                continue
            
            total_days = sum(r.duration for r in repairs_with_duration)
            avg_days = total_days / len(repairs_with_duration) if repairs_with_duration else 0
            
            repair_duration.append({
                'repair_type': rtype,
                'avg_days': avg_days
            })
        
        # Sort by average duration (descending)
        repair_duration.sort(key=lambda x: x['avg_days'], reverse=True)
        
        return repair_duration
    
    def _get_monthly_costs(self, repairs):
        """Get monthly repair costs for the specified year"""
        monthly_costs = defaultdict(float)
        for repair in repairs:
            month_idx = repair.start_date.month - 1
            # Convert decimal to float
            monthly_costs[month_idx] += float(repair.repair_cost)
        
        costs = [monthly_costs.get(m, 0) for m in range(12)]
        return costs 