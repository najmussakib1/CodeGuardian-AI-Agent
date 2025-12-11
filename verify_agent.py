import os
import sys
from dotenv import load_dotenv

# Check for API Key first
load_dotenv()
key = os.getenv("GROQ_API_KEY")
if not key or key.startswith("your_groq"):
    print("SKIPPING_VERIFICATION: No valid Groq API Key found.")
    sys.exit(0)

try:
    import agent
    
    filepath = "repo_to_watch/test_bad_code.py"
    print(f"Running agent on {filepath}")
    result = agent.run_agent(filepath)
    print("Agent Result:", result)
    
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
