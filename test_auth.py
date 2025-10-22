#!/usr/bin/env python3
"""
Test script to check API authentication
"""
import requests
import json

# Test with a dummy token to see the error
headers = {
    'Authorization': 'Bearer dummy-token',
    'Content-Type': 'application/json'
}

try:
    response = requests.get('http://localhost:6070/api/businesses', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")