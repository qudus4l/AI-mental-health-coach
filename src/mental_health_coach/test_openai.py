"""Test OpenAI API connection."""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("OPENAI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key length: {len(api_key) if api_key else 0}")

if api_key:
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=50
        )
        
        print(f"\n✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n❌ Error calling OpenAI API: {e}")
        print(f"Error type: {type(e).__name__}")
else:
    print("\n❌ No API key found in environment") 