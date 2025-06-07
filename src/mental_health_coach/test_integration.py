"""Integration test script to verify all API endpoints are working."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(name, success, message=""):
    """Print test result with color."""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {name}")
    if message:
        print(f"  {YELLOW}{message}{RESET}")


def test_health_check():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200
        print_test("Health Check", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False


def test_login():
    """Test login and return token."""
    try:
        # OAuth2 expects form data
        data = {
            "username": TEST_EMAIL,  # OAuth2 uses 'username' for email
            "password": TEST_PASSWORD
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data=data,  # Use data, not json for form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_test("Login", True, f"Token received: {token[:20]}...")
            return token
        else:
            print_test("Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test("Login", False, str(e))
        return None


def test_user_profile(token):
    """Test getting user profile."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print_test("Get User Profile", True, f"User: {user['email']}")
            return True
        else:
            print_test("Get User Profile", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get User Profile", False, str(e))
        return False


def test_conversations(token):
    """Test conversation endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create conversation
    try:
        data = {
            "title": "Test Conversation",
            "is_formal_session": False
        }
        response = requests.post(
            f"{BASE_URL}/api/conversations/",
            json=data,
            headers=headers
        )
        
        if response.status_code == 201:
            conversation = response.json()
            conversation_id = conversation["id"]
            print_test("Create Conversation", True, f"ID: {conversation_id}")
            
            # Test sending a message
            message_data = {
                "content": "Hello, I'm feeling a bit anxious today.",
                "is_from_user": True
            }
            
            msg_response = requests.post(
                f"{BASE_URL}/api/conversations/{conversation_id}/messages",
                json=message_data,
                headers=headers
            )
            
            if msg_response.status_code == 201:
                result = msg_response.json()
                print_test("Send Message", True, f"User message ID: {result['message']['id']}")
                
                if 'ai_message' in result:
                    print_test("AI Response", True, f"AI responded with {len(result['ai_message']['content'])} chars")
                
                return conversation_id
            else:
                print_test("Send Message", False, f"Status: {msg_response.status_code}, Error: {msg_response.text}")
                return None
        else:
            print_test("Create Conversation", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Conversation Tests", False, str(e))
        return None


def test_dashboard(token):
    """Test dashboard endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print_test("Dashboard Stats", True, f"Total conversations: {stats.get('total_conversations', 0)}")
            return True
        else:
            print_test("Dashboard Stats", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Dashboard Stats", False, str(e))
        return False


def main():
    """Run all integration tests."""
    print(f"\n{YELLOW}=== Mental Health Coach API Integration Tests ==={RESET}\n")
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health check
    if not test_health_check():
        print(f"\n{RED}Server is not responding. Make sure it's running on {BASE_URL}{RESET}")
        return
    
    print()
    
    # Test authentication
    token = test_login()
    if not token:
        print(f"\n{RED}Authentication failed. Cannot continue with other tests.{RESET}")
        return
    
    print()
    
    # Test user profile
    test_user_profile(token)
    
    print()
    
    # Test conversations
    conversation_id = test_conversations(token)
    
    print()
    
    # Test dashboard
    test_dashboard(token)
    
    print(f"\n{GREEN}=== Tests Complete ==={RESET}\n")


if __name__ == "__main__":
    main() 