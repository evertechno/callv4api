#!/usr/bin/env python3
"""
MSP API Debug Script
This script helps diagnose connection issues with the MSP API
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway"

def test_endpoint(api_key, endpoint, method="GET", data=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "x-msp-api-key": api_key
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:12]}...{api_key[-4:]}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        
        return response.status_code == 200 or response.status_code == 201
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("The server might not be reachable or the URL is incorrect")
        return False
    except requests.exceptions.Timeout as e:
        print(f"\n❌ TIMEOUT ERROR: {e}")
        print("The server took too long to respond")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return False

def main():
    print("MSP API Debug Script")
    print("="*60)
    
    # Get API key
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your MSP API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    if not api_key.startswith("msp_"):
        print("⚠️  Warning: API key doesn't start with 'msp_'")
    
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {api_key[:12]}...{api_key[-4:]}")
    
    # Test different possible URL formats
    print("\n" + "="*60)
    print("TESTING DIFFERENT URL FORMATS")
    print("="*60)
    
    urls_to_test = [
        "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/enboxes",
        "https://vwhxcuylitpawxjplfnq.supabase.co/functions/v1/msp-gateway/stats",
        "https://vwhxcuylitpawxjplfnq.functions.supabase.co/msp-gateway/enboxes",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "x-msp-api-key": api_key
    }
    
    for url in urls_to_test:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code != 404:
                print(f"  ✅ Found! This might be the correct URL")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test main endpoints
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    results = {}
    
    # Test GET /enboxes
    results['GET /enboxes'] = test_endpoint(api_key, "/enboxes")
    
    # Test GET /stats
    results['GET /stats'] = test_endpoint(api_key, "/stats")
    
    # Test GET /usage
    results['GET /usage'] = test_endpoint(api_key, "/usage")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for endpoint, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {endpoint}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! Your API connection is working.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("1. Edge function not deployed")
        print("2. Incorrect API key")
        print("3. API key expired or inactive")
        print("4. Wrong Supabase project URL")
        print("5. Edge function name mismatch")

if __name__ == "__main__":
    main()
