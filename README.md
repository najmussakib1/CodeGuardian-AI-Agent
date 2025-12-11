🛡️ CodeGuardian

A lightweight automated code-quality and patch-validation pipeline.

📌 Overview

CodeGuardian watches a target repository, validates incoming patches, applies them safely, runs static analysis + tests, and reports the results.
It is designed to simulate a mini CI/CD workflow locally.

🚀 Features

🔍 Patch Parsing & Verification
Ensures patches follow correct unified diff format.

🧩 Automatic Patch Application
Applies patches to the target repo safely using git apply.

🧪 Code Quality Checks
Runs flake8 and pytest over the patched repository.

📂 Repository Watcher
Processes patches from an incoming directory.

📝 Structured JSON Output
Saves pipeline results with status messages.

📁 Project Structure
agent/
 ├── main.py                # Main pipeline runner
 ├── patcher.py             # Patch parsing + git apply logic
 ├── utils.py               # File IO, flake8, pytest helpers
 └── ...
repo_to_watch/
 ├── example.py
 ├── test_example.py
 └── ...
incoming_patches/
 └── *.patch

