from WBAdmin_Script import create_image
from email_notify import send_backup_email
import os, json, sys, time
from win11toast import toast
from storage import upload_backup

'''
This script will be called from the task scheduler and run the backup task
'''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "backup_config.json")
LOG_FILE = os.path.join(BASE_DIR, "backup_log.txt")
NOTIFY = True

def notify(title, message):
    if NOTIFY:
        toast(title, message, duration="short")

def write_log(message):
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

config = load_config()
if not config:
    sys.exit()

# Load config fields
s3_access_key    = config.get("s3_access_key", "")
s3_secret_key    = config.get("s3_secret_key", "")
s3_bucket_name   = config.get("s3_bucket_name", "")
storage_path     = config.get("storage_path", "")
schedule         = config.get("schedule", "Daily")
weekday          = config.get("weekday", "Mon")
hour             = config.get("hour", "12")
minute           = config.get("minute", "00")
ampm             = config.get("ampm", "AM")
last_backup      = config.get("last_backup", "Never")
region_name      = config.get("s3_region", "us-east-1")
endpoint_url     = config.get("s3_endpoint_url", "")
email_enabled    = config.get("email_enabled", False)
notify_on_success = config.get("notify_on_success", True)
notify_on_failure = config.get("notify_on_failure", True)

source_drive = "C:"  # let user choose?
target_drive = storage_path[:2]

# Timing
backup_start = time.time()
print(f"[BACKUP] Started: {time.strftime('%H:%M:%S')}")

try:
    notify("3-2-1 Backup Tool", "Backup Starting")
    write_log("Backup started")

    create_image(source_drive=source_drive, target_drive=target_drive)

    # Update last backup time
    last_backup = time.strftime("%Y-%m-%d %H:%M:%S")

    elapsed = time.time() - backup_start
    print(f"[BACKUP] Finished: {time.strftime('%H:%M:%S')}")
    print(f"[BACKUP] Total:    {elapsed:.2f}s  ({elapsed/60:.2f} min)")
    write_log(f"Backup completed in {elapsed:.2f}s")

    # Save config with updated last_backup
    config_data = {
        "s3_access_key":     s3_access_key,
        "s3_secret_key":     s3_secret_key,
        "s3_bucket_name":    s3_bucket_name,
        "storage_path":      storage_path,
        "schedule":          schedule,
        "weekday":           weekday,
        "hour":              hour,
        "minute":            minute,
        "ampm":              ampm,
        "last_backup":       last_backup,
        "s3_region":         region_name,
        "s3_endpoint_url":   endpoint_url,
        "email_enabled":     email_enabled,
        "email_recipient":   config.get("email_recipient", ""),
        "email_sender":      config.get("email_sender", ""),
        "email_password":    config.get("email_password", ""),
        "notify_on_success": notify_on_success,
        "notify_on_failure": notify_on_failure,
        "notify_on_missed":  config.get("notify_on_missed", True),
        "auto_backup":       config.get("auto_backup", True),
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

    notify("3-2-1 Backup Tool", "Backup Completed Successfully!")

    # S3 Upload
    upload_backup(
        target_drive          = target_drive,
        aws_access_key_id     = s3_access_key,
        aws_secret_access_key = s3_secret_key,
        region_name           = region_name,
        bucket_name           = s3_bucket_name,
        endpoint_url          = endpoint_url
    )
    write_log("S3 upload completed")
    notify("3-2-1 Backup Tool", "Backup Uploaded to Cloud!")

    # Success email
    if email_enabled and notify_on_success:
        send_backup_email(
            success = True,
            details = (
                f"Backup completed at {last_backup}\n"
                f"Duration: {elapsed/60:.1f} minutes\n"
                f"Storage: {storage_path}\n"
                f"S3 Bucket: {s3_bucket_name}"
            )
        )
        write_log("Success email sent")

except Exception as e:
    elapsed = time.time() - backup_start
    notify("3-2-1 Backup Tool", "Backup Failed")
    write_log(f"Scheduled backup failed: {e}")

    # Failure email
    if email_enabled and notify_on_failure:
        try:
            send_backup_email(success=False, details=str(e))
            write_log("Failure email sent")
        except Exception as email_err:
            write_log(f"Failed to send failure email: {email_err}")