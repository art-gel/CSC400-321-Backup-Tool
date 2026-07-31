import boto3, os, math
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

PART_SIZE = 1024 * 1024 * 64  # 64MB

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
        connect_timeout=300,
        request_checksum_calculation='when_required',
        response_checksum_validation='when_required',
        s3={'addressing_style': 'path'}
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
        multipart_threshold=PART_SIZE, 
        max_concurrency=3,
        multipart_chunksize=PART_SIZE,
        use_threads=True
    )
    
    # walk all files in WindowsImageBackup, including the WindowsImageBackup folder
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_folder)

            s3_key = f"WindowsImageBackup/{relative_path}".replace("\\", "/")
            
            upload_one_file(s3_client, local_path, bucket_name, s3_key)

    print("All uploads complete.")


def upload_one_file(s3_client, local_path, bucket_name, s3_key):
    '''
    Uploads a single file, splitting it into parts (multipart upload) and
    resuming from wherever a previous attempt left off, if any.
    
    Notes:
    LocalStack shows an example of S3 storage backend in its file
    structure. <localstack folder>/state/s3/<bucket name> should have a
    folder for oversized files that contains the numbered parts of the 
    files. We will force all files to behave that way (broken into parts) 
    and ask if a part already exists before trying to upload it. 
    
    '''
    file_size = os.path.getsize(local_path)
    total_parts = math.ceil(file_size / PART_SIZE)
 
    # check to see if file exists in S3, then get how much of it was done already
    upload_id = find_existing_upload(s3_client, bucket_name, s3_key)
 
    if upload_id:
        # resume upload
        done_parts = get_uploaded_parts(s3_client, bucket_name, s3_key, upload_id)
        print(f"Resuming {s3_key}: {len(done_parts)}/{total_parts} part(s) already uploaded.")
    else:
        # create new upload
        response = s3_client.create_multipart_upload(Bucket=bucket_name, Key=s3_key)
        upload_id = response["UploadId"]
        done_parts = {}
 
    # open the file and check each part to see if it already exists in 'done_parts'
    with open(local_path, "rb") as f:
        for part_number in range(1, total_parts + 1):
            if part_number in done_parts:
                continue  
 
            f.seek((part_number - 1) * PART_SIZE)
            chunk = f.read(PART_SIZE)
 
            response = s3_client.upload_part(
                Bucket=bucket_name,
                Key=s3_key,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=chunk,
            )
            # ETag is a hash of the file
            # keep it for verification later (S3 handles that)
            done_parts[part_number] = response["ETag"]
            print(f"  {s3_key}: part {part_number}/{total_parts} uploaded")
 
    # after completing the file, pass S3 a list of all the parts numbers and our ETags for verification
    parts_list = [{"PartNumber": n, "ETag": done_parts[n]} for n in sorted(done_parts)]
    s3_client.complete_multipart_upload(
        Bucket=bucket_name,
        Key=s3_key,
        UploadId=upload_id,
        MultipartUpload={"Parts": parts_list},
    )
    print(f"Uploading.. {s3_key} completed")
 
 
def find_existing_upload(s3_client, bucket_name, s3_key):
    # Returns the upload_id of an unfinished multipart upload for this key, or None.
    response = s3_client.list_multipart_uploads(Bucket=bucket_name, Prefix=s3_key)
    for upload in response.get("Uploads", []):
        if upload["Key"] == s3_key:
            return upload["UploadId"]
    return None
 
 
def get_uploaded_parts(s3_client, bucket_name, s3_key, upload_id):
    # Returns dictionary for parts S3 already has for this upload_id.
    # {part_number: ETag}
    response = s3_client.list_parts(Bucket=bucket_name, Key=s3_key, UploadId=upload_id)
    return {p["PartNumber"]: p["ETag"] for p in response.get("Parts", [])}
 
