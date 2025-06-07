"""Full conversation test with the AI mental health coach."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Colors for output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_message(sender, message):
    """Print a message with formatting."""
    if sender == "User":
        print(f"\n{BLUE}User:{RESET} {message}")
    else:
        print(f"\n{GREEN}Ami (AI Coach):{RESET} {message}")


def main():
    print(f"\n{YELLOW}=== AI Mental Health Coach - Full Conversation Demo ==={RESET}\n")
    
    # 1. Login
    print("Logging in...")
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
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Logged in successfully")
    
    # 2. Create a conversation
    print("\nCreating a new conversation...")
    conv_data = {
        "title": "Demo Conversation",
        "is_formal_session": False
    }
    response = requests.post(
        f"{BASE_URL}/api/conversations/",
        json=conv_data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"Failed to create conversation: {response.text}")
        return
    
    conversation = response.json()
    conversation_id = conversation["id"]
    print(f"✓ Created conversation ID: {conversation_id}")
    
    # 3. Have a conversation
    print(f"\n{YELLOW}--- Starting Conversation ---{RESET}")
    
    messages = [
        "Hi, I've been feeling really anxious lately about work.",
        "I keep worrying that I'm not good enough and that my colleagues think I'm incompetent.",
        "What are some techniques I can use to manage these anxious thoughts?",
        "Thank you, that's helpful. I'll try the 5-4-3-2-1 technique next time I feel overwhelmed."
    ]
    
    for user_message in messages:
        print_message("User", user_message)
        
        # Send message
        msg_data = {
            "content": user_message,
            "is_from_user": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/messages",
            json=msg_data,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            if 'ai_message' in result:
                print_message("Ami", result['ai_message']['content'])
                
                # Check for crisis detection
                if result.get('crisis_detected'):
                    print(f"\n{YELLOW}⚠️  Crisis detected - resources provided{RESET}")
        else:
            print(f"\nError sending message: {response.text}")
            break
        
        # Small delay between messages
        time.sleep(1)
    
    # 4. End conversation
    print(f"\n{YELLOW}--- Ending Conversation ---{RESET}")
    response = requests.put(
        f"{BASE_URL}/api/conversations/{conversation_id}/end",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ Conversation ended successfully")
    
    # 5. Show conversation stats
    print(f"\n{YELLOW}--- Conversation Summary ---{RESET}")
    response = requests.get(
        f"{BASE_URL}/api/dashboard/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Total conversations: {stats.get('total_conversations', 0)}")
        print(f"Total messages: {stats.get('total_messages', 0)}")
        
        if 'mood_trends' in stats and stats['mood_trends']:
            print(f"Recent mood: {stats['mood_trends'][0].get('mood_score', 'N/A')}/10")
    
    print(f"\n{GREEN}=== Demo Complete ==={RESET}")
    print(f"\nYou can now login to the frontend at http://localhost:3000 with:")
    print(f"Email: {TEST_EMAIL}")
    print(f"Password: {TEST_PASSWORD}")
    print(f"\nYour conversation will be visible in the conversations list!")


if __name__ == "__main__":
    main() 