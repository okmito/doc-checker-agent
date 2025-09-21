import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras, AuthenticationError

# --- Setup ---
# Load environment variables from .env file in the current directory
print("Attempting to load .env file...")
load_dotenv()

api_key = os.environ.get("CEREBRAS_API_KEY")

if not api_key:
    print("\nFATAL: CEREBRAS_API_KEY not found in environment variables.")
    print("Please ensure a .env file exists in the 'backend' directory and contains the key.")
else:
    print(f"API Key loaded successfully. Key starts with: {api_key[:4]}...")

    # --- Direct API Call ---
    try:
        print("\nInitializing Cerebras client...")
        client = Cerebras(api_key=api_key)

        print("Sending a test message to model 'llama-3.3-70b'...")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello, world!"}],
            model="llama-3.3-70b",
            max_completion_tokens=10,
        )

        print("\n✅ SUCCESS: Connection to Cerebras API is working!")
        print(f"AI Response: {response.choices[0].message.content}")

    except AuthenticationError as e:
        print("\n❌ FAILED: AuthenticationError.")
        print("This means the API key is incorrect or invalid. Please double-check it.")
        print(f"Details: {e}")

    except Exception as e:
        print(f"\n❌ FAILED: An unexpected error occurred.")
        print("This could be a network issue (firewall, proxy) or a problem with the SDK.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Details: {e}")

