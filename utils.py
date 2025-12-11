import os
import subprocess
import json
import difflib
from datetime import datetime

RESULTS_FILE = "results.json"

def lint_file(filepath):
    """
    Runs pylint on the given file and returns the output and score.
    """
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    
    # Run pylint
    # We use a custom format to easily parse, or just capture stdout
    result = subprocess.run(
        ["pylint", filepath, "--output-format=text"],
        capture_output=True,
        text=True
    )
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def apply_fix(filepath, new_content):
    """
    Overwrites the file with new content.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error applying fix: {e}")
        return False

def generate_patch(original_content, new_content, filepath):
    """
    Generates a unified diff patch.
    """
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm=""
    )
    return "".join(diff)

def log_result(filepath, errors, fixed_code, patch):
    """
    Logs the result to results.json
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "filepath": filepath,
        "errors": errors,
        "patch": patch,
        "status": "fixed" if fixed_code else "failed"
    }

    data = []
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass
    
    data.append(entry)
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_patch_to_disk(filepath, patch_content):
    """
    Saves the patch content to a file in the 'patches' directory.
    """
    PATCHES_DIR = "patches"
    if not os.path.exists(PATCHES_DIR):
        os.makedirs(PATCHES_DIR)
        
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    patch_filename = f"{filename}_{timestamp}.patch"
    patch_path = os.path.join(PATCHES_DIR, patch_filename)
    
    with open(patch_path, 'w', encoding='utf-8') as f:
        f.write(patch_content)
    
    return patch_path
