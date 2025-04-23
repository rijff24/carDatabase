from app import create_app
from app.reports.standard.sales_performance import SalesPerformanceReport
from app.reports.standard.profit_margin import ProfitMarginReport
from app.reports.standard.repair_analysis import RepairAnalysisReport
from app.reports.standard.inventory_aging import InventoryAgingReport
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal JSON serialization"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def test_report(report_class, params=None, report_name=""):
    """Test a report class by generating a report with the given parameters"""
    print(f"\n{'='*50}")
    print(f"Testing {report_name or report_class.__name__}")
    print(f"{'='*50}")
    
    try:
        # Initialize report with parameters
        report = report_class(**(params or {}))
        
        # Generate report data
        data = report.generate()
        
        # Print summary of the report data
        print("Report generation successful!")
        print(f"Generated {len(data)} data points")
        
        # Print some key metrics if available
        if "total_sales_count" in data:
            print(f"Total Sales: {data['total_sales_count']}")
        if "total_revenue" in data:
            print(f"Total Revenue: {data['total_revenue']}")
        if "total_profit" in data:
            print(f"Total Profit: {data['total_profit']}")
        if "total_repairs" in data:
            print(f"Total Repairs: {data['total_repairs']}")
        if "total_cost" in data:
            print(f"Total Cost: {data['total_cost']}")
        if "total_cars" in data:
            print(f"Total Cars: {data['total_cars']}")
        
        # Print all data as JSON for detailed inspection
        print("\nDetailed Report Data:")
        print(json.dumps(data, indent=2, cls=DecimalEncoder))
        
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all report classes"""
    app = create_app()
    
    with app.app_context():
        # Test Sales Performance Report
        test_report(
            SalesPerformanceReport,
            {'period': 'monthly', 'year': 2023},
            "Sales Performance Report (2023)"
        )
        
        test_report(
            SalesPerformanceReport,
            {'period': 'monthly', 'year': 2024},
            "Sales Performance Report (2024)"
        )
        
        # Test Profit Margin Report
        test_report(
            ProfitMarginReport,
            {'timeframe': 'last_30_days'},
            "Profit Margin Report (last 30 days)"
        )
        
        test_report(
            ProfitMarginReport,
            {'timeframe': 'all_time'},
            "Profit Margin Report (all time)"
        )
        
        # Test Repair Analysis Report
        test_report(
            RepairAnalysisReport,
            {'year': 2023},
            "Repair Analysis Report (2023)"
        )
        
        # Test Inventory Aging Report
        test_report(
            InventoryAgingReport,
            {},
            "Inventory Aging Report"
        )

if __name__ == "__main__":
    main() 