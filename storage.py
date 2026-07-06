import boto3
from pathlib import Path
from config import get_settings


def upload(encrypted_path: Path, bucket: str, region: str, on_progress=None) -> str:
    settings = get_settings()
    client = boto3.client("s3", region_name=region, endpoint_url=settings.endpoint_url)
    key = f"backups/{encrypted_path.name}"
    total  = encrypted_path.stat().st_size
    sent = 0

    def report(bytes_sent):
        nonlocal sent
        sent+= bytes_sent
        if on_progress:
            on_progress(sent/total)
    client.upload_file(Filename=str(encrypted_path), Bucket=bucket, Key=key, Callback=report)

    return key

# bytes_so_far / total_size


# reverse upload, needed by restore pipeline. 
def download(key: str, bucket: str, region: str) -> Path:
    settings = get_settings()
    client = boto3.client("s3", region_name=region, endpoint_url=settings.endpoint_url)
    # save the downloaded file in the current folder, named after the object
    dest = Path(Path(key).name)
    client.download_file(Bucket=bucket, Key=key, Filename=str(dest))
    return dest
