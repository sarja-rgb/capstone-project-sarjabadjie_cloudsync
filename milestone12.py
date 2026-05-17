<<<<<<< HEAD
import os
import platform
from datetime import datetime

print("=== CloudSync Manager - Milestone 12 Verification ===")
print(f"Run time: {datetime.now()}")
print(f"Platform: {platform.platform()}")
print(f"Working directory: {os.getcwd()}")

required_files = [
    "main.py",
    "README.md",
    "MILESTONE12.md",
    "requirements.txt",
    "config_db.py",
    "s3_client.py",
    "milestone12_ui.py",
]

print("\n[1] Required File Check")
missing = []

for file in required_files:
    if os.path.exists(file):
        print(f" - {file}: OK")
    else:
        print(f" - {file}: MISSING")
        missing.append(file)

print("\n[2] ZIP Package Check")

zip_file = "CloudSyncManager_M12.zip"

if os.path.exists(zip_file):
    print(f" - {zip_file}: FOUND")
else:
    print(f" - {zip_file}: NOT FOUND")

print("\n[3] Verification Result")

if len(missing) == 0:
    print("RESULT: PASS - Milestone 12 verification completed successfully.")
else:
    print("RESULT: WARNING - Some files are missing.")
=======
import os
import platform
from datetime import datetime

print("=== CloudSync Manager - Milestone 12 Verification ===")
print(f"Run time: {datetime.now()}")
print(f"Platform: {platform.platform()}")
print(f"Working directory: {os.getcwd()}")

required_files = [
    "main.py",
    "README.md",
    "MILESTONE12.md",
    "requirements.txt",
    "config_db.py",
    "s3_client.py",
    "milestone12_ui.py",
]

print("\n[1] Required File Check")
missing = []

for file in required_files:
    if os.path.exists(file):
        print(f" - {file}: OK")
    else:
        print(f" - {file}: MISSING")
        missing.append(file)

print("\n[2] ZIP Package Check")

zip_file = "CloudSyncManager_M12.zip"

if os.path.exists(zip_file):
    print(f" - {zip_file}: FOUND")
else:
    print(f" - {zip_file}: NOT FOUND")

print("\n[3] Verification Result")

if len(missing) == 0:
    print("RESULT: PASS - Milestone 12 verification completed successfully.")
else:
    print("RESULT: WARNING - Some files are missing.")
>>>>>>> d67ca98e (Milestone 12: add verification and UI demo code)
