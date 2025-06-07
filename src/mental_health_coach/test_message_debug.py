"""Debug script to test message sending."""

import requests
import json
import traceback

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Login
print("1. Logging in...")
login_data = {
    "username": TEST_EMAIL,
    "password": TEST_PASSWORD
}
response = requests.post(
    f"{BASE_URL}/api/auth/token",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Logged in")

# Create conversation
print("\n2. Creating conversation...")
conv_data = {
    "title": "Debug Conversation",
    "is_formal_session": False
}
response = requests.post(
    f"{BASE_URL}/api/conversations/",
    json=conv_data,
    headers=headers
)

if response.status_code != 201:
    print(f"Failed to create conversation: {response.text}")
    exit(1)

conversation_id = response.json()["id"]
print(f"✓ Created conversation ID: {conversation_id}")

# Send a simple message
print("\n3. Sending message...")
msg_data = {
    "content": "Hello",
    "is_from_user": True
}

try:
    response = requests.post(
        f"{BASE_URL}/api/conversations/{conversation_id}/messages",
        json=msg_data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✓ Success!")
        print(f"User Message ID: {result['message']['id']}")
        if 'ai_message' in result:
            print(f"AI Response: {result['ai_message']['content'][:100]}...")
    else:
        print(f"\n✗ Error!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n✗ Exception occurred!")
    print(f"Error: {str(e)}")
    traceback.print_exc()

print("\nDone.") 