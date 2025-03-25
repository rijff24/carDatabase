import requests
import json

BASE_URL = 'http://localhost:5000'

def print_response(response):
    """Print response in a formatted way"""
    print(f"\nStatus Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))

def test_validate_params():
    print("\n=== Testing Parameter Validation ===")
    
    # Test 1: Valid request
    print("\nTest 1: Valid request")
    response = requests.get(f"{BASE_URL}/test/validate-params", params={
        'year': 2024,
        'month': 3,
        'period': 'daily',
        'email': 'test@example.com'
    })
    print_response(response)
    
    # Test 2: Missing required parameter
    print("\nTest 2: Missing required parameter")
    response = requests.get(f"{BASE_URL}/test/validate-params", params={
        'month': 3
    })
    print_response(response)
    
    # Test 3: Invalid type
    print("\nTest 3: Invalid type")
    response = requests.get(f"{BASE_URL}/test/validate-params", params={
        'year': 'not_a_number',
        'month': 3
    })
    print_response(response)

def test_validate_json():
    print("\n=== Testing JSON Validation ===")
    
    # Test 1: Valid request
    print("\nTest 1: Valid request")
    response = requests.post(f"{BASE_URL}/test/validate-json", json={
        'name': 'Test Car',
        'price': 19999.99,
        'email': 'test@example.com',
        'is_active': True
    })
    print_response(response)
    
    # Test 2: Missing required field
    print("\nTest 2: Missing required field")
    response = requests.post(f"{BASE_URL}/test/validate-json", json={
        'price': 19999.99
    })
    print_response(response)
    
    # Test 3: Invalid type
    print("\nTest 3: Invalid type")
    response = requests.post(f"{BASE_URL}/test/validate-json", json={
        'name': 'Test Car',
        'price': 'not_a_number',
        'email': 'test@example.com'
    })
    print_response(response)

def test_validate_custom():
    print("\n=== Testing Custom Validation ===")
    
    # Test 1: Valid request
    print("\nTest 1: Valid request")
    response = requests.get(f"{BASE_URL}/test/validate-custom", params={
        'email': 'test@example.com',
        'price': '19999.99'
    })
    print_response(response)
    
    # Test 2: Invalid email
    print("\nTest 2: Invalid email")
    response = requests.get(f"{BASE_URL}/test/validate-custom", params={
        'email': 'invalid-email',
        'price': '19999.99'
    })
    print_response(response)
    
    # Test 3: Invalid price
    print("\nTest 3: Invalid price")
    response = requests.get(f"{BASE_URL}/test/validate-custom", params={
        'email': 'test@example.com',
        'price': '-100'
    })
    print_response(response)

if __name__ == '__main__':
    test_validate_params()
    test_validate_json()
    test_validate_custom() 