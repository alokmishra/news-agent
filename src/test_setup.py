import os
import sys
from dotenv import load_dotenv

def check_setup():
    print("--- Checking Setup ---")
    
    # 1. Check Imports
    try:
        import langchain_google_genai
        import mailjet_rest
        import langgraph
        print("[+] Dependencies imported successfully.")
    except ImportError as e:
        print(f"[-] Missing dependency: {e}")
        sys.exit(1)

    # 2. Check Environment
    load_dotenv()
    required_keys = [
        "GOOGLE_API_KEY",
        "MAILJET_API_KEY",
        "MAILJET_SECRET_KEY", 
        "SENDER_EMAIL",
        "RECIPIENT_EMAIL"
    ]
    
    missing = []
    for key in required_keys:
        val = os.getenv(key)
        if not val or "your_" in val: # Check for default placeholders
            missing.append(key)
    
    if missing:
        print(f"[-] The following .env keys are missing or still placeholders: {', '.join(missing)}")
        print("    Please update .env with real values to run the agent.")
    else:
        print("[+] Environment variables seem correctly set.")

if __name__ == "__main__":
    check_setup()
