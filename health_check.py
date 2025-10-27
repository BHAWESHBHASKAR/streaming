#!/usr/bin/env python3
"""
Health Check Script
Use this to verify your deployment is working correctly
"""

import requests
import sys

def check_health(url):
    """Check if the application is running"""
    try:
        response = requests.get(f"{url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Application is running!")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Streaming: {'Yes' if data.get('is_running') else 'No'}")
            print(f"   FPS: {data.get('fps', 0)}")
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to application: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://127.0.0.1:8080"
    
    print(f"🔍 Checking health of: {url}")
    print("=" * 50)
    
    if check_health(url):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
