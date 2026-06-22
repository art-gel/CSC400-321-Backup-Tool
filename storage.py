"""Step 3 of the pipeline: upload to AWS S3 (the offsite "1" of 3-2-1).

REAL IMPLEMENTATION (your job): use boto3's multipart upload to stream the
encrypted file to S3 in chunks with resumable parts. Point boto3 at LocalStack
during testing so you don't touch real AWS.

Returns the S3 object key so the job record can reference it later (for restore).
"""

import time
from pathlib import Path


def upload(encrypted_path: Path, bucket: str, region: str, on_progress=None) -> str:
    """Upload `encrypted_path` to `bucket`. Returns the S3 key."""
    client = boto3.client("s3",region_name=region)
    key = f"backups/{encrypted_path.name}"
    client.upload_file(Filename=str(encrypted_path), Bucket=bucket, Key=key)
    
    for pct in (0.33, 0.66, 1.0):
        time.sleep(0.05)
        if on_progress:
            on_progress(pct)
    return key
