import boto3, os
from pathlib import Path
# from config import get_settings
from botocore.exceptions import ClientError
from botocore.config import Config
from boto3.s3.transfer import TransferConfig

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



def create_bucket(s3_client, bucket_name):
    try:
        # check if the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"INFO: Bucket '{bucket_name}' already exists.")
    except ClientError as e:
        # check if the error is a 404 (Not Found)
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"INFO: Bucket '{bucket_name}' not found. Creating it...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"INFO: Bucket '{bucket_name}' created successfully.")
        else:
            # If it's a 403 (Forbidden) or other error, re-raise it
            raise e


def upload_backup(target_drive, aws_access_key_id, aws_secret_access_key, region_name, bucket_name, endpoint_url):
    '''
    this function is simmilar to upload() but it can upload an entire backup folder using a multipart upload

    it currently lacks the progress reporting that the original upload function used. not sure how to impliment it yet -Troy
    '''
    print("Uploading..")

    local_folder = os.path.join(target_drive, "WindowsImageBackup") # folder does not change

    if not os.path.exists(local_folder):
        print(f"ERROR: {local_folder} not found!")
        return


    client_config = Config(
        retries={'max_attempts': 3},
        read_timeout=300,  # Increase to 5 minutes
        connect_timeout=300
    )

    s3_client = boto3.client("s3", 
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,      
        region_name=region_name,
        endpoint_url=endpoint_url,
        config=client_config)

    create_bucket(s3_client, bucket_name)

    # Configure the transfer
    # 64MB threshold for multipart, 3 threads for parallel uploads
    transfer_config = TransferConfig(
        multipart_threshold=1024 * 1024 * 64, 
        max_concurrency=3,
        multipart_chunksize=1024 * 1024 * 64,
        use_threads=True
    )
    
    # walk all files in WindowsImageBackup, including the WindowsImageBackup folder
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_folder)

            s3_key = f"WindowsImageBackup/{relative_path}".replace("\\", "/")
            
            s3_client.upload_file(
                local_path, 
                bucket_name, 
                s3_key,
                Config=transfer_config
            )
            print(f"Uploading.. {s3_key} completed")
    print("All uploads complete.")