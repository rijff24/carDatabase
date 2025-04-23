import requests
import json
from datetime import datetime
import os

def test_reports_api():
    """
    Test all report API endpoints and save the responses to JSON files.
    Run this while the application is running on port 5000.
    """
    base_url = "http://localhost:5000/reports/api"
    output_dir = "report_api_test"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Test sales performance report
    endpoints = [
        {
            "name": "sales_performance_2023",
            "url": f"{base_url}/sales-performance?period=monthly&year=2023",
        },
        {
            "name": "sales_performance_2024",
            "url": f"{base_url}/sales-performance?period=monthly&year=2024",
        },
        {
            "name": "repair_analysis_2023",
            "url": f"{base_url}/repair-analysis?year=2023",
        },
        {
            "name": "inventory_aging_all",
            "url": f"{base_url}/inventory-aging?status=all",
        },
        {
            "name": "profit_margin_30days",
            "url": f"{base_url}/profit-margin?timeframe=last_30_days",
        },
        {
            "name": "profit_margin_alltime",
            "url": f"{base_url}/profit-margin?timeframe=all_time",
        },
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint['name']}")
            response = requests.get(endpoint['url'])
            
            if response.status_code == 200:
                data = response.json()
                
                # Save to file
                filename = os.path.join(output_dir, f"{endpoint['name']}.json")
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"  ✓ Success - saved to {filename}")
                results[endpoint['name']] = "Success"
            else:
                print(f"  ✗ Failed with status code: {response.status_code}")
                results[endpoint['name']] = f"Failed: {response.status_code}"
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results[endpoint['name']] = f"Error: {str(e)}"
    
    # Print summary
    print("\nTest Summary:")
    print("="*50)
    for name, result in results.items():
        status = "✓" if "Success" in result else "✗"
        print(f"{status} {name}: {result}")
    
    return results

if __name__ == "__main__":
    print("Testing report API endpoints...")
    test_reports_api()
    print("\nDone!") 