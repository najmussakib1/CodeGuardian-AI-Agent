import streamlit as st
import os
import json
import agent
import utils
from glob import glob

st.set_page_config(page_title="CodeGuardian", layout="wide")
st.title("🛡️ CodeGuardian Agent")

REPO_DIR = "repo_to_watch"
RESULTS_FILE = "results.json"

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
if "scan_results" not in st.session_state:
    st.session_state.scan_results = {}

# Sidebar
st.sidebar.header("Monitored Files")
if os.path.exists(REPO_DIR):
    files = glob(os.path.join(REPO_DIR, "*.py"))
    for f in files:
        st.sidebar.text(os.path.basename(f))
else:
    st.sidebar.warning(f"Directory {REPO_DIR} not found!")

# Main Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Control Panel")
    
    # Step 1: Scan
    if st.button("Scan Code for Errors"):
        if not files:
            st.warning("No python files found to scan.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            st.session_state.scan_results = {}
            
            for i, f in enumerate(files):
                status_text.text(f"Scanning {os.path.basename(f)}...")
                try:
                    # Run dry run
                    res = agent.run_agent(f, dry_run=True)
                    st.session_state.scan_results[f] = res
                except Exception as e:
                    st.error(f"Error scanning {f}: {e}")
                
                progress_bar.progress((i + 1) / len(files))
            
            status_text.text("Scan Completed!")

    # Display Scan Results
    if st.session_state.scan_results:
        st.markdown("### Scan Results")
        
        for filepath, res in st.session_state.scan_results.items():
            filename = os.path.basename(filepath)
            
            with st.expander(f"Result: {filename}", expanded=True):
                if res["status"] == "clean":
                    st.success("✅ Clean (No errors found)")
                elif res["status"] == "needs_fix" or res.get("patch"): # agent might return needs_fix or have a patch
                    st.error("❌ Errors Detected")
                    st.code(res.get("errors", "Unknown errors"))
                    
                    if res.get("patch"):
                        st.subheader("Proposed Fix (Patch)")
                        st.code(res["patch"], language='diff')
                        
                        # Apply Fix Button for this specific file
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.button(f"Apply Fix for {filename}", key=f"btn_{filename}"):
                             # Apply changes
                             utils.apply_fix(filepath, res["fixed_code"])
                             # Save patch
                             patch_path = utils.save_patch_to_disk(filepath, res["patch"])
                             # Log result
                             utils.log_result(filepath, res["errors"], res["fixed_code"], res["patch"])
                             
                             st.success(f"Fixed applied and patch saved to {patch_path}!")
                             # Clear result key to force re-scan or update status?
                             # For now, just show success. 
                             
                else:
                    st.warning(f"Status: {res['status']}")

with col2:
    st.subheader("Activity Log")
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r") as f:
                logs = json.load(f)
            
            # Show latest first
            for log in reversed(logs):
                with st.expander(f"Fix: {os.path.basename(log['filepath'])} @ {log['timestamp']}"):
                    st.text("Errors detected:")
                    st.code(log['errors'])
                    st.text("Patch applied:")
                    st.code(log['patch'], language='diff')
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("No logs available yet.")

# Instructions
st.markdown("---")
st.info(f"Place python files in the `{REPO_DIR}` directory. 1. Click 'Scan Code'. 2. Review Errors & Patch. 3. Click 'Apply Fix' to repair.")
