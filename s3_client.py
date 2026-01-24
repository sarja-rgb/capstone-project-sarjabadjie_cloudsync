"""
s3_client.py

Thin boto3 wrapper used by CloudSync Manager Milestone 1.

Responsibilities:
- Build an S3 client from an AWS profile and/or region.
- Provide a simple "list objects" helper for testing connectivity.

NOTE: This assumes AWS credentials are available on the machine,
e.g., via `aws configure` or environment variables.
"""

from typing import List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def build_s3_client(profile_name: Optional[str] = None, region_name: Optional[str] = None):
    """Build and return a boto3 S3 client."""
    session_kwargs = {}
    if profile_name:
        session_kwargs["profile_name"] = profile_name

    session = boto3.Session(**session_kwargs)
    client_kwargs = {}
    if region_name:
        client_kwargs["region_name"] = region_name

    return session.client("s3", **client_kwargs)


def list_objects_simple(client, bucket: str, prefix: Optional[str] = None) -> List[str]:
    """
    Return a list of object keys in the given bucket/prefix.

    Used only for Milestone 1 as a simple connectivity test.
    """
    try:
        if prefix:
            resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        else:
            resp = client.list_objects_v2(Bucket=bucket)

        contents = resp.get("Contents", [])
        return [obj["Key"] for obj in contents]
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Error listing objects in bucket '{bucket}': {exc}")
