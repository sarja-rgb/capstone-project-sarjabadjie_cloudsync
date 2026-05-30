"""
s3_smoke_test.py
Simple AWS S3 connectivity smoke test (list a prefix).

Run from repo root:
    python demo_tests/s3_smoke_test.py --profile cloudsync-demo --bucket fsocloudstore1 --prefix testuploads/
"""
import argparse
import boto3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--prefix", default="")
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile)
    s3 = session.client("s3")

    print("=== S3 SMOKE TEST ===")
    print("Bucket:", args.bucket)
    print("Prefix:", args.prefix)

    resp = s3.list_objects_v2(Bucket=args.bucket, Prefix=args.prefix, MaxKeys=5)
    contents = resp.get("Contents", [])
    for obj in contents:
        print(" -", obj["Key"])

    print("PASS: S3 list_objects_v2 succeeded (items may be empty).")


if __name__ == "__main__":
    main()
