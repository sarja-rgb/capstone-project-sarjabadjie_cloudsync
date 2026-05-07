from pathlib import Path

import sys

import platform

from datetime import datetime



REQUIRED\_FILES = \[

&#x20;   "main.py",

&#x20;   "requirements.txt",

&#x20;   "README.md",

&#x20;   "MILESTONE11.md",

&#x20;   "SoundSoar.pdf",

&#x20;   "performance\_cpu\_m10\_ui.html",

&#x20;   "performance\_cpu\_main.html",

&#x20;   "milestone11\_ui.py",

]



ZIP\_FILE = "CloudSyncManager\_M11.zip"



def check\_file(path: Path) -> str:

&#x20;   return "OK" if path.exists() else "MISSING"



def main():

&#x20;   root = Path.cwd()



&#x20;   print("=== CloudSync Manager - Milestone 11 Verification ===")

&#x20;   print(f"Run time: {datetime.now()}")

&#x20;   print(f"Repo root: {root}")

&#x20;   print()



&#x20;   print("\[1] Environment check:")

&#x20;   print(f" - Python: {sys.version.split()\[0]}")

&#x20;   print(f" - Platform: {platform.platform()}")

&#x20;   print(f" - Working dir: {root}")

&#x20;   print()



&#x20;   print("\[2] Required file check:")

&#x20;   missing = \[]

&#x20;   for file\_name in REQUIRED\_FILES:

&#x20;       path = root / file\_name

&#x20;       status = check\_file(path)

&#x20;       print(f" - {file\_name}: {status}")

&#x20;       if status == "MISSING":

&#x20;           missing.append(file\_name)



&#x20;   print()

&#x20;   print("\[3] Build ZIP check:")

&#x20;   zip\_path = root / ZIP\_FILE

&#x20;   if zip\_path.exists():

&#x20;       print(f" - {ZIP\_FILE}: FOUND")

&#x20;   else:

&#x20;       print(f" - {ZIP\_FILE}: MISSING")

&#x20;       missing.append(ZIP\_FILE)



&#x20;   print()

&#x20;   if missing:

&#x20;       print("RESULT: Some Milestone 11 files are missing.")

&#x20;       print("Missing files:")

&#x20;       for item in missing:

&#x20;           print(f" - {item}")

&#x20;       return 1



&#x20;   print("RESULT: PASS - Milestone 11 verification files are present.")

&#x20;   return 0



if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   raise SystemExit(main())

