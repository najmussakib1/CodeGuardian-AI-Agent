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

⚙️ Installation
1️⃣ Clone this repository
git clone https://github.com/your-username/codeguardian.git
cd codeguardian

2️⃣ Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

▶️ Running the Pipeline

To run CodeGuardian manually:

python agent/main.py


The pipeline will:

Read the latest .patch file from incoming_patches/

Validate patch format

Apply patch to repo_to_watch/

Run flake8 & pytest

Write results to output.json

🧪 Example Patch Format

A correct unified diff patch looks like:

--- example.py
+++ example.py
@@ -1,5 +1,5 @@
 def add(a, b):
-    return a % b
+    return a + b

🛠 Requirements

Python 3.8+

Git installed

flake8

pytest

📊 Output Example

output.json:

{
  "patch_applied": true,
  "flake8_passed": true,
  "pytest_passed": true,
  "message": "Patch applied and all checks passed successfully."
}

🧑‍💻 Contributing

Pull requests are welcome!
For major changes, open an issue first to discuss what you’d like to change.

📜 License

MIT License — free to use and modify.
