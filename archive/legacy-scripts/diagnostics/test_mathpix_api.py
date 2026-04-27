#!/usr/bin/env python3
"""
Simple test script to verify Mathpix API is working correctly
"""
import requests
from config.config import get_settings

def test_mathpix_connection():
    """Test basic Mathpix API connection"""
    settings = get_settings()
    
    print("Testing Mathpix API connection...")
    print(f"URL: {settings.mathpix_url}")
    print(f"App ID: {settings.mathpix_app_id}")
    print(f"App Key: {'*' * len(settings.mathpix_app_key)}")
    
    # Test with a simple ping to check credentials
    headers = {
        "app_id": settings.mathpix_app_id,
        "app_key": settings.mathpix_app_key
    }
    
    # Try a simple test API call to check if credentials work
    test_url = f"{settings.mathpix_url}/v3/user"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Mathpix API connection successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"[ERROR] Mathpix API connection failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        
    # Also test with a simple ping to the PDF endpoint to see current status
    pdf_url = f"{settings.mathpix_url}/v3/pdf"
    
    try:
        response = requests.get(pdf_url, headers=headers, timeout=10)
        print(f"\nPDF Endpoint Status Code: {response.status_code}")
        if response.status_code == 405:  # GET not allowed, but connection OK
            print("✅ PDF endpoint is accessible (method not allowed is expected)")
        else:
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ PDF endpoint test failed: {e}")

if __name__ == "__main__":
    test_mathpix_connection()