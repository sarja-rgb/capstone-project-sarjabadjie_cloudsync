# CloudSync Manager – Milestone 1 Starter

This folder contains a minimal, working Milestone 1 prototype for your Capstone project.

## What this build does

- Opens a PyQt desktop window.
- Lets you configure:
  - Local folder
  - S3 bucket
  - Optional prefix, AWS profile, and region
- Saves the configuration into a local SQLite database: `cloudsync_metadata.db`.
- Provides a **Test S3 Connection** button that:
  - Builds a boto3 S3 client from the profile/region.
  - Attempts to list objects in the given bucket/prefix.
  - Shows the first keys (if any) in the GUI output pane.

This matches the Milestone 1 expectations for:
- Basic GUI + configuration
- Initial AWS S3 integration
- Metadata foundation (starting SQLite schema)

## How to run

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
venv\\Scripts\\activate   # on Windows
# or
source venv/bin/activate  # on macOS/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure AWS credentials are configured (e.g., via AWS CLI):

```bash
aws configure
```

or set up a named profile and use that in the GUI.

4. Run the app:

```bash
python main.py
```

5. Use the GUI to:
   - Choose a local folder.
   - Enter an S3 bucket (and optional prefix/profile/region).
   - Click **Save Configuration**.
   - Click **Test S3 Connection** to verify that the bucket is reachable.
