"""Test frontend functionality by logging in as test user."""

import requests
import json

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Frontend and backend URLs
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

print("=== Frontend Integration Test ===\n")

# 1. Test backend login
print("1. Testing backend login...")
login_data = {
    "username": TEST_EMAIL,
    "password": TEST_PASSWORD
}

response = requests.post(
    f"{BACKEND_URL}/api/auth/token",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ Login successful! Token: {token[:30]}...")
    print("\n2. You can now:")
    print(f"   - Go to {FRONTEND_URL}/login")
    print(f"   - Login with email: {TEST_EMAIL}")
    print(f"   - Login with password: {TEST_PASSWORD}")
    print("\n3. After logging in, you should be able to:")
    print("   - View the dashboard")
    print("   - Create new conversations")
    print("   - Send messages (Note: AI responses require OPENAI_API_KEY)")
    print("\n4. If you encounter issues:")
    print("   - Check browser console for errors")
    print("   - Visit /dashboard/debug for debugging info")
else:
    print(f"✗ Login failed: {response.status_code}")
    print(f"Response: {response.text}")

print("\n=== Test Complete ===") 