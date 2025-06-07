#!/usr/bin/env python3
"""Health check script for verifying Railway deployment.

This script checks if the API is running and accessible.
"""

import sys
import requests
from typing import Optional


def check_health(base_url: str) -> bool:
    """Check if the API is healthy.
    
    Args:
        base_url: The base URL of the API.
        
    Returns:
        bool: True if healthy, False otherwise.
    """
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print(f"✅ API is healthy: {data}")
                return True
        print(f"❌ API returned unexpected response: {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API: {e}")
        return False


def check_docs(base_url: str) -> bool:
    """Check if API documentation is accessible.
    
    Args:
        base_url: The base URL of the API.
        
    Returns:
        bool: True if accessible, False otherwise.
    """
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        print(f"❌ API docs returned: {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to access API docs: {e}")
        return False


def main(base_url: Optional[str] = None) -> int:
    """Run health checks.
    
    Args:
        base_url: The base URL to check. Defaults to production URL.
        
    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    if not base_url:
        base_url = input("Enter the Railway app URL (e.g., https://your-app.railway.app): ").strip()
    
    print(f"\n🔍 Checking health of: {base_url}\n")
    
    health_ok = check_health(base_url)
    docs_ok = check_docs(base_url)
    
    if health_ok and docs_ok:
        print("\n✅ All checks passed! Your deployment is working correctly.")
        return 0
    else:
        print("\n❌ Some checks failed. Please check your deployment logs.")
        return 1


if __name__ == "__main__":
    exit_code = main(sys.argv[1] if len(sys.argv) > 1 else None)
    sys.exit(exit_code) 