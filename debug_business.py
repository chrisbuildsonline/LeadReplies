#!/usr/bin/env python3
"""
Debug script to check business data
"""
import requests

# Test the debug endpoint
try:
    response = requests.get('http://localhost:6070/debug/businesses')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test the main businesses endpoint (this will fail without auth)
try:
    response = requests.get('http://localhost:6070/api/businesses')
    print(f"Businesses endpoint status: {response.status_code}")
    if response.status_code != 401:  # Expected to be 401 without auth
        print(f"Unexpected response: {response.text}")
except Exception as e:
    print(f"Error: {e}")