# template for AWS link for third party storage 
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
