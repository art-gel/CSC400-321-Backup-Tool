from WBAdmin_Script import create_image
import os, json, sys, time
from win11toast import toast

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

aws_access_key = config.get("aws_access_key", "")
aws_secret_key = config.get("aws_secret_key", "")
s3_bucket_name = config.get("s3_bucket_name", "")
storage_path = config.get("storage_path", "")
schedule = config.get("schedule", "Daily")
weekday = config.get("weekday", "Mon")
hour = config.get("hour", "12")
minute = config.get("minute", "00")
ampm = config.get("ampm", "AM")
last_backup = config.get("last_backup", "Never")

source_drive = "C:" #let user choose?
target_drive = storage_path[:2]
try:
    notify("3-2-1 Backup Tool", "Backup Starting")
    create_image(source_drive=source_drive, target_drive=target_drive)

    # update last backup
    last_backup = time.strftime("%Y-%m-%d %H:%M:%S")

    # save config
    config = {
        "aws_access_key": aws_access_key,
        "aws_secret_key": aws_secret_key,
        "s3_bucket_name": s3_bucket_name,
        "storage_path": storage_path,
        "schedule": schedule,
        "weekday": weekday,
        "hour": hour,
        "minute": minute,
        "ampm": ampm,
        "last_backup": last_backup
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    notify("3-2-1 Backup Tool", "Backup Completed Successfully!")


except Exception as e:
    notify("3-2-1 Backup Tool", "Backup Failed")
    write_log(f"Scheduled backup failed: {e}")



