

import WBAdmin_Script
import encryption
import storage
from config import get_settings
from models import JobStatus

JOBS = {}


def run_backup(job_id, passphrase):
    # runs ONE backup from start to finish.
    # # passphrase arrives as an argument, gets used, and is never written to the job 
    settings = get_settings()
    job = JOBS.get(job_id)
    if job is None:
        return

    try:
        # stage 1: copy the drive into an image file
        job.status = JobStatus.imaging
        job.progress = 0.0
        image_path = WBAdmin_Script.create_image(job.source_drive)
        print("Stage 1:(in-progress) - copying the drive to an image file")

        # stage 2: lock the image with the passphrase
        job.status = JobStatus.encrypting
        job.progress = 0.25
        enc_path = encryption.encrypt_file(image_path, passphrase)
        print("Stage 2:(in-Progress) - Encrypting image file with passphrase")

        # stage 3: send the LOCKED file to S3
        job.status = JobStatus.uploading
        job.progress = 0.50
        job.s3_key = storage.upload(enc_path, settings.s3_bucket, settings.aws_region)
        print("Stage 3:(in-progress) - uploading encrypted file to AWS Bucket")

        # done
        job.status = JobStatus.completed
        job.progress = 1.0
        print("Completed!")

    except Exception as error:
        # error if any of the stages breaks 
        job.status = JobStatus.failed
        job.error = str(error)
        print("Error in one of the stages has occured!")

    


def run_restore(job_id, passphrase):
    
    settings = get_settings()
    job = JOBS.get(job_id)
    if job is None:
        return

    try:
        # stage 1: pull the locked file back down from S3
        job.status = JobStatus.downloading
        job.progress = 0.0
        enc_path = storage.download(job.s3_key, settings.s3_bucket, settings.aws_region)
        print("file from S3 buckeet is being downloaded")

        # stage 2: unlock it (fails loudly if the passphrase is wrong)
        job.status = JobStatus.decrypting
        job.progress = 0.5
        image_path = encryption.decrypt_file(enc_path, passphrase)
        print("Un-Encrypting in progress")
        

        # done,communicates where their recovered image is
        job.restored_file = str(image_path)
        job.status = JobStatus.completed
        job.progress = 1.0
        print("restore complete ")

    except Exception as error:
        job.status = JobStatus.failed
        job.error = str(error)
        print("an error has occured in one of the stages")

    # WARNING NOTE: this restore recovers the image FILE. 
    # It does not write the image back onto a live drive.(wbadmin start recovery) is destructive and must be tested carefully on a
    # spare Windows machine before i automate it.
