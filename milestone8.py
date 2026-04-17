"""
milestone8.py - CloudSync Manager / CloudSync Insight
Milestone 8: S3 adapter + local scan + one-way sync prototype (demo entry point)

This script is a lightweight, CLI demo runner for Milestone 8 so the milestone
has an explicit code artifact in the repo.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from s3_client import build_s3_client, list_objects_simple

# NOTE: Adjust import name if your repo uses a different module/class name.
client = build_s3_client(profile_name=profile or None, region_name=region or None)
keys = list_objects_simple(client, bucket=bucket, prefix=prefix or None)

print(f"[S3 Test] Objects returned: {len(keys)}")
for k in keys[:10]:
    print(f"  - {k}")
if len(keys) > 10:
    print("  ...")

def scan_local_folder(folder: str) -> List[str]:
    """Return a simple list of relative file paths for demo purposes."""
    root = Path(folder)
    if not root.exists():
        raise FileNotFoundError(f"Local folder not found: {folder}")

    files = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(root)))
    return files


def main() -> None:
    # Use env vars so you don't hardcode credentials in code.
    local_folder = os.environ.get("CLOUDSYNC_LOCAL_FOLDER", "").strip()
    bucket = os.environ.get("CLOUDSYNC_S3_BUCKET", "").strip()
    prefix = os.environ.get("CLOUDSYNC_S3_PREFIX", "").strip()
    profile = os.environ.get("AWS_PROFILE", "").strip()
    region = os.environ.get("AWS_REGION", "").strip()

    print("=== Milestone 8 Demo Runner ===")

    if local_folder:
        print(f"[Local Scan] Folder: {local_folder}")
        files = scan_local_folder(local_folder)
        print(f"[Local Scan] Files found: {len(files)}")
        for f in files[:10]:
            print(f"  - {f}")
        if len(files) > 10:
            print("  ...")
    else:
        print("[Local Scan] Skipped (set CLOUDSYNC_LOCAL_FOLDER env var to enable).")

    if not bucket:
        print("[S3 Test] Skipped (set CLOUDSYNC_S3_BUCKET env var).")
        return

    client = build_s3_client(profile_name=profile or None, region_name=region or None)
keys = list_objects_simple(client, bucket=bucket, prefix=prefix or None)

print(f"[S3 Test] Objects returned: {len(keys)}")
for k in keys[:10]:
    print(f"  - {k}")
if len(keys) > 10:
    print("  ...")

    print(f"[S3 Test] Bucket: {bucket}")
    print(f"[S3 Test] Prefix: {prefix or '(none)'}")
    print(f"[S3 Test] AWS_PROFILE: {profile or '(default)'}  AWS_REGION: {region or '(default)'}")

    # This assumes S3Client can be constructed with profile/region, adjust if needed.
    client = S3Client(profile_name=profile or None, region_name=region or None)  # type: ignore

    # This assumes the client has a list method. Adjust method name if different.
    results = client.list_objects(bucket=bucket, prefix=prefix or None)  # type: ignore

    print(f"[S3 Test] Objects returned: {len(results)}")
    for k in results[:10]:
        print(f"  - {k}")
    if len(results) > 10:
        print("  ...")

    print("=== End Milestone 8 Demo ===")


if __name__ == "__main__":
    main()