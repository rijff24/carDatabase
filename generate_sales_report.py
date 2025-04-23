#!/usr/bin/env python
from app import create_app, db
from app.reports.standard.sales_performance import SalesPerformanceReport
from datetime import datetime
import argparse
import json
import decimal
import os
import sys

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal JSON serialization"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def print_section(title):
    """Print a section title"""
    print("\n" + "-" * 50)
    print(f" {title}")
    print("-" * 50)

def print_metric(label, value, format_str=None):
    """Print a metric with proper formatting"""
    if isinstance(value, decimal.Decimal) and format_str:
        formatted_value = format_str.format(value)
    elif isinstance(value, decimal.Decimal):
        formatted_value = f"${float(value):,.2f}"
    elif isinstance(value, (int, float)) and format_str:
        formatted_value = format_str.format(value)
    else:
        formatted_value = str(value)
        
    print(f"{label:<30}: {formatted_value}")

def generate_chart(data, period, year, output_file=None):
    """Generate a bar chart visualization of the sales performance data"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract period data
        periods = [p['period_name'] for p in data['sales_by_period']]
        sales_counts = [p['count'] for p in data['sales_by_period']]
        revenues = [float(p['revenue'])/1000 for p in data['sales_by_period']]  # Convert to thousands
        profits = [float(p['profit'])/1000 for p in data['sales_by_period']]  # Convert to thousands
        
        # Set up bar positions
        x = np.arange(len(periods))
        width = 0.25
        
        # Create bars
        ax.bar(x - width, sales_counts, width, label='Sales (Count)', color='#4472C4')
        ax.bar(x, revenues, width, label='Revenue (Thousands)', color='#ED7D31')
        ax.bar(x + width, profits, width, label='Profit (Thousands)', color='#70AD47')
        
        # Add labels and title
        ax.set_title(f'Sales Performance Report - {period.capitalize()} {year}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Period', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(periods)
        ax.legend()
        
        # Add value labels
        for i, v in enumerate(sales_counts):
            ax.text(i - width, v + 0.5, str(v), ha='center', fontsize=9)
            
        for i, v in enumerate(revenues):
            if v > 0:
                ax.text(i, v + 0.5, f"${v:.1f}K", ha='center', fontsize=9)
            
        for i, v in enumerate(profits):
            if v > 0:
                ax.text(i + width, v + 0.5, f"${v:.1f}K", ha='center', fontsize=9)
        
        # Set grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add summary text
        summary_text = (
            f"Total Sales: {data['total_sales_count']}\n"
            f"Total Revenue: ${float(data['total_revenue']):,.2f}\n"
            f"Total Profit: ${float(data['total_profit']):,.2f}\n"
            f"Profit Margin: {float(data['profit_margin']):.2f}%"
        )
        plt.figtext(0.02, 0.02, summary_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Adjust layout
        plt.tight_layout()
        
        # Save or show chart
        if output_file:
            # Create directory if needed
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {output_file}")
        else:
            os.makedirs("reports", exist_ok=True)
            chart_file = f"reports/sales_performance_{year}_{period}_chart.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {chart_file}")
        
        plt.close()
        return True
    except ImportError:
        print("Warning: Could not generate chart because matplotlib is not installed.")
        print("To install matplotlib, run: pip install matplotlib")
        return False
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return False

def generate_sales_report(period='monthly', year=None, output_format='console', output_file=None, chart=False, chart_file=None):
    """
    Generate a sales performance report with the specified parameters
    
    Args:
        period (str): Report period - 'monthly', 'quarterly', or 'yearly'
        year (int): Year to report on - defaults to current year
        output_format (str): Output format - 'console', 'json', or 'csv'
        output_file (str): Path to output file (if json or csv format)
        chart (bool): Whether to generate a chart visualization
        chart_file (str): Path to chart output file
    """
    # Set default year to current year if not provided
    if year is None:
        year = datetime.now().year
    
    # Create and initialize app context
    app = create_app()
    
    with app.app_context():
        print_header(f"Generating Sales Performance Report ({period}, {year})")
        
        # Create report instance
        report = SalesPerformanceReport(period=period, year=year)
        
        try:
            # Generate report data
            data = report.generate()
            
            # Output handling
            if output_format == 'json':
                # Default output file
                if not output_file:
                    os.makedirs("reports", exist_ok=True)
                    output_file = f"reports/sales_performance_{year}_{period}.json"
                else:
                    # Create directory if needed
                    output_dir = os.path.dirname(output_file)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                
                # Write to JSON file
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2, cls=DecimalEncoder)
                    
                print(f"Report saved to {output_file}")
                
                # Generate chart if requested
                if chart:
                    generate_chart(data, period, year, chart_file)
                    
                return True
                
            elif output_format == 'csv':
                # Default output file
                if not output_file:
                    os.makedirs("reports", exist_ok=True)
                    output_file = f"reports/sales_performance_{year}_{period}.csv"
                else:
                    # Create directory if needed
                    output_dir = os.path.dirname(output_file)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                
                # Write main metrics to CSV
                with open(output_file, 'w') as f:
                    # Write header
                    f.write("Metric,Value\n")
                    
                    # Write main metrics
                    f.write(f"Period,{period}\n")
                    f.write(f"Year,{year}\n")
                    f.write(f"Total Sales,{data['total_sales_count']}\n")
                    f.write(f"Total Revenue,{float(data['total_revenue'])}\n")
                    f.write(f"Total Profit,{float(data['total_profit'])}\n")
                    f.write(f"Average Margin,{float(data['average_margin'])}\n")
                    
                    # Write period data
                    f.write("\nPeriod,Sales Count,Revenue,Profit,Margin\n")
                    for period_data in data['sales_by_period']:
                        f.write(f"{period_data['period_name']},{period_data['count']}," +
                                f"{float(period_data['revenue'])},{float(period_data['profit'])}," +
                                f"{float(period_data['margin'])}\n")
                    
                    # Write dealer data
                    f.write("\nDealer,Sales Count,Revenue,Profit,Margin\n")
                    for dealer in data['sales_by_dealer']:
                        f.write(f"{dealer['dealer_name']},{dealer['sales_count']}," +
                                f"{float(dealer['total_revenue'])},{float(dealer['total_profit'])}," +
                                f"{float(dealer['margin'])}\n")
                
                print(f"Report saved to {output_file}")
                
                # Generate chart if requested
                if chart:
                    generate_chart(data, period, year, chart_file)
                
                return True
            
            else:  # console output
                # Print summary
                print_section("Summary")
                print_metric("Report Period", period.capitalize())
                print_metric("Year", year)
                print_metric("Report Date", data['report_date'])
                print_metric("Total Sales", data['total_sales_count'])
                print_metric("Total Revenue", data['total_revenue'])
                print_metric("Total Profit", data['total_profit'])
                print_metric("Profit Margin", data['profit_margin'], "{:.2f}%")
                
                # Print period breakdown
                print_section(f"Sales by {period.capitalize()}")
                for period_data in data['sales_by_period']:
                    print(f"\n{period_data['period_name']} ({period_data['count']} sales):")
                    print_metric("  Revenue", period_data['revenue'])
                    print_metric("  Profit", period_data['profit'])
                    print_metric("  Margin", period_data['margin'], "{:.2f}%")
                    print_metric("  Sales Change", period_data['sales_change'], "{:+.2f}%")
                
                # Print dealer performance
                print_section("Dealer Performance")
                for dealer in data['sales_by_dealer']:
                    print(f"\n{dealer['dealer_name']} ({dealer['sales_count']} sales):")
                    print_metric("  Revenue", dealer['total_revenue'])
                    print_metric("  Profit", dealer['total_profit'])
                    print_metric("  Average Sale", dealer['average_sale'])
                    print_metric("  Margin", dealer['margin'], "{:.2f}%")
                
                # Print top models
                print_section("Top Models")
                for idx, model in enumerate(data['top_models'], 1):
                    print(f"{idx}. {model['make']} {model['model']}: {model['count']} sales, " +
                          f"${float(model['average_price']):,.2f} avg. price")
                
                # Print year comparison
                print_section("Year-over-Year Comparison")
                prev = data['previous_year_comparison']
                print(f"{year} vs {prev['previous_year']}:")
                print_metric("Sales", f"{prev['current_sales']} vs {prev['previous_sales']}", 
                             "({:+.2f}%)".format(prev['sales_change']))
                print_metric("Revenue", f"${float(prev['current_revenue']):,.2f} vs ${float(prev['previous_revenue']):,.2f}", 
                             "({:+.2f}%)".format(prev['revenue_change']))
                print_metric("Profit", f"${float(prev['current_profit']):,.2f} vs ${float(prev['previous_profit']):,.2f}", 
                             "({:+.2f}%)".format(prev['profit_change']))
                
                print("\nReport generated successfully.")
                
                # Generate chart if requested
                if chart:
                    generate_chart(data, period, year, chart_file)
                
                return True
                
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Parse command line arguments and generate report"""
    parser = argparse.ArgumentParser(description='Generate Sales Performance Report')
    parser.add_argument('--period', type=str, choices=['monthly', 'quarterly', 'yearly'], 
                        default='monthly', help='Reporting period')
    parser.add_argument('--year', type=int, default=datetime.now().year,
                       help='Year to report on (default: current year)')
    parser.add_argument('--format', type=str, choices=['console', 'json', 'csv'],
                       default='console', help='Output format')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path (for json or csv format)')
    parser.add_argument('--chart', action='store_true',
                       help='Generate a chart visualization')
    parser.add_argument('--chart-file', type=str, default=None,
                       help='Path to chart output file')
    
    args = parser.parse_args()
    
    success = generate_sales_report(
        period=args.period,
        year=args.year,
        output_format=args.format,
        output_file=args.output,
        chart=args.chart,
        chart_file=args.chart_file
    )
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 