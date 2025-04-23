from app import create_app
from app.reports.standard.sales_performance import SalesPerformanceReport
from app.reports.standard.profit_margin import ProfitMarginReport
from app.reports.standard.repair_analysis import RepairAnalysisReport
from app.reports.standard.inventory_aging import InventoryAgingReport
from flask import render_template
import os
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal JSON serialization"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def save_report(report_class, params=None, filename="", report_name=""):
    """Generate a report and save it to a file"""
    print(f"Generating {report_name or report_class.__name__}...")
    
    try:
        # Create report instance
        report = report_class(**(params or {}))
        
        # Generate report data
        data = report.generate()
        
        # Create output directory if it doesn't exist
        os.makedirs("report_output", exist_ok=True)
        
        # Save as JSON
        json_filename = f"report_output/{filename or report_class.__name__}.json"
        with open(json_filename, "w") as f:
            json.dump(data, f, indent=2, cls=DecimalEncoder)
        
        print(f"Report data saved to {json_filename}")
        
        # Render HTML if template exists
        if hasattr(report, 'template_path') and report.template_path:
            template_filename = f"report_output/{filename or report_class.__name__}.html"
            
            # Initialize Flask app to use render_template
            app = create_app()
            with app.app_context():
                html = render_template(report.template_path, **data)
                
                with open(template_filename, "w", encoding="utf-8") as f:
                    f.write(html)
                
                print(f"HTML report saved to {template_filename}")
        
        return True
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Generate all reports and save them to files"""
    app = create_app()
    
    with app.app_context():
        # Generate Sales Performance Reports
        save_report(
            SalesPerformanceReport,
            {'period': 'monthly', 'year': 2023},
            "sales_performance_2023",
            "Sales Performance Report (2023)"
        )
        
        save_report(
            SalesPerformanceReport,
            {'period': 'monthly', 'year': 2024},
            "sales_performance_2024",
            "Sales Performance Report (2024)"
        )
        
        # Generate Profit Margin Reports
        save_report(
            ProfitMarginReport,
            {'timeframe': 'last_30_days'},
            "profit_margin_30days",
            "Profit Margin Report (last 30 days)"
        )
        
        save_report(
            ProfitMarginReport,
            {'timeframe': 'all_time'},
            "profit_margin_alltime",
            "Profit Margin Report (all time)"
        )
        
        # Generate Repair Analysis Report
        save_report(
            RepairAnalysisReport,
            {'year': 2023},
            "repair_analysis_2023",
            "Repair Analysis Report (2023)"
        )
        
        # Generate Inventory Aging Report
        save_report(
            InventoryAgingReport,
            {},
            "inventory_aging",
            "Inventory Aging Report"
        )
        
        print("\nAll reports generated successfully.")
        print("You can find the reports in the report_output directory.")

if __name__ == "__main__":
    main() 