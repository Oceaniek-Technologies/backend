#!/usr/bin/env python
import requests
import json
import sys

def test_api(base_url="http://localhost:5000"):
    """
    Test the Shorties API endpoints
    """
    print(f"Testing Shorties API at {base_url}")
    
    # Test the root endpoint
    try:
        response = requests.get(base_url)
        print(f"Root endpoint: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"Error accessing root endpoint: {str(e)}")
    
    # Test the swagger documentation endpoint
    try:
        response = requests.get(f"{base_url}/swagger/")
        print(f"Swagger docs: {response.status_code} - {'Available' if response.status_code == 200 else 'Not available'}")
    except Exception as e:
        print(f"Error accessing swagger endpoint: {str(e)}")
    
    # Test the API endpoints
    endpoints = [
        "/api/v1/users/search/",
        "/api/v1/videos/",
        "/api/v1/social/notifications/unread-count/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"Endpoint {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  Response: {json.dumps(response.json(), indent=2)[:100]}...")
        except Exception as e:
            print(f"Error accessing {endpoint}: {str(e)}")
    
    print("\nAPI test completed.")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_api(base_url)