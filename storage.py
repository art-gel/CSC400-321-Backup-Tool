# template for AWS link for third party storage 
import boto3
from pathlib import Path

def report(bytes_sent):
    total  = encrypted_path.stat().st_size
    sent = 0

def upload(encrypted_path: Path, bucket: str, region: str, on_progress=None) -> str:
    client = boto3.client("s3",region_name=region)
    key = f"backups/{encrypted_path.name}"
    client.upload_file(Filename=str(encrypted_path), Bucket=bucket, Key=key)
    
    return key
    
# bytes_so_far / total_size