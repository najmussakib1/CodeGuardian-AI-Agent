
import os
import agent
import utils
import shutil

# Setup
REPO_DIR = "repo_to_watch"
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)

BAD_CODE_FILE = os.path.join(REPO_DIR, "test_bad_code_verify.py")
BAD_CODE_CONTENT = """
def hello():
  print("Hello") # Indentation error likely if I mix tabs/spaces or just bad style, but let's make a clear syntax error or missing import
  import non_existent_module
"""

# Reset
if os.path.exists(BAD_CODE_FILE):
    os.remove(BAD_CODE_FILE)

with open(BAD_CODE_FILE, "w") as f:
    f.write(BAD_CODE_CONTENT)

print("--- Starting Verification ---")

# 1. Dry Run
print("Running agent in dry_run mode...")
result = agent.run_agent(BAD_CODE_FILE, dry_run=True)

print(f"Status: {result['status']}")
print(f"Errors found: {bool(result['errors'])}")
print(f"Patch generated: {bool(result['patch'])}")

# Check file content - MUST BE UNCHANGED
with open(BAD_CODE_FILE, "r") as f:
    current_content = f.read()

if current_content == BAD_CODE_CONTENT:
    print("SUCCESS: File content is unchanged after dry run.")
else:
    print("FAILURE: File content was changed!")
    exit(1)

# 2. Apply Fix (Simulating Button Click)
if result['status'] == "needs_fix" or result.get("patch"):
    print("Applying fix manually...")
    utils.apply_fix(BAD_CODE_FILE, result["fixed_code"])
    patch_path = utils.save_patch_to_disk(BAD_CODE_FILE, result["patch"])
    
    print(f"Patch saved to: {patch_path}")
    
    # Check file content - MUST BE CHANGED
    with open(BAD_CODE_FILE, "r") as f:
        new_content = f.read()
        
    if new_content != BAD_CODE_CONTENT:
        print("SUCCESS: File content is updated.")
    else:
        print("FAILURE: File content was NOT updated.")
        exit(1)
        
    # Check patch file exists
    if os.path.exists(patch_path):
        print("SUCCESS: Patch file exists.")
    else:
        print("FAILURE: Patch file not found.")
        exit(1)

print("--- Verification Complete ---")
