from app.reports.base.report import Report
from app.reports.standard.sales_performance import SalesPerformanceReport
from app.reports.standard.repair_analysis import RepairAnalysisReport
from app.reports.standard.inventory_aging import InventoryAgingReport
from app.reports.standard.profit_margin import ProfitMarginReport

# Dictionary mapping report names to report classes
REPORT_REGISTRY = {
    'sales_performance': SalesPerformanceReport,
    'repair_analysis': RepairAnalysisReport,
    'inventory_aging': InventoryAgingReport,
    'profit_margin': ProfitMarginReport
}

# Function to get report by name
def get_report(report_name):
    """
    Get a report class by name
    """
    if report_name in REPORT_REGISTRY:
        return REPORT_REGISTRY[report_name]
    
    raise ValueError(f"Report '{report_name}' not found")

# Register a custom report
def register_report(report_name, report_class):
    """
    Register a custom report class
    """
    if report_name in REPORT_REGISTRY:
        raise ValueError(f"Report '{report_name}' already exists")
    
    REPORT_REGISTRY[report_name] = report_class 