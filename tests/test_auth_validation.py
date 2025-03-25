import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = 'http://localhost:5000'

def test_login_validation():
    """Test login form validation"""
    print("\n=== Testing Login Validation ===")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Get CSRF token
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test 1: Valid login credentials
    print("\nTest 1: Valid login credentials")
    data = {
        'username': 'testuser123',
        'password': 'TestPass123!',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Get new CSRF token for next test
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test 2: Invalid username format
    print("\nTest 2: Invalid username format")
    data = {
        'username': 'te',  # Too short
        'password': 'TestPass123!',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Get new CSRF token for next test
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test 3: Invalid password format
    print("\nTest 3: Invalid password format")
    data = {
        'username': 'testuser123',
        'password': 'weak',  # Too weak
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Get new CSRF token for next test
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test 4: Missing required fields
    print("\nTest 4: Missing required fields")
    data = {
        'username': 'testuser123',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Get new CSRF token for next test
    response = session.get(f'{BASE_URL}/auth/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Test 5: Invalid next URL
    print("\nTest 5: Invalid next URL")
    data = {
        'username': 'testuser123',
        'password': 'TestPass123!',
        'remember_me': True,
        'csrf_token': csrf_token
    }
    response = session.post(f'{BASE_URL}/auth/login?next=http://malicious-site.com', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_login_validation() 