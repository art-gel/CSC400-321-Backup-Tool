import os, re, time, win32api, win32file

BACKUP_FOLDER_NAME = "WindowsImageBackup"

# Format bytes
def format_bytes(size_bytes):
    gb = size_bytes / (1024 ** 3)
    if gb >= 1024:
        return f"{gb / 1024:.2f} TB"
    return f"{gb:.2f} GB"

# Find existing backup on a drive
def find_existing_backup(drive_path):
    if not drive_path:
        return None

    backup_path = os.path.join(drive_path, BACKUP_FOLDER_NAME)
    if not os.path.isdir(backup_path):
        return None

    try:
        modified = os.path.getmtime(backup_path)
    except OSError:
        modified = None

    total_size = 0
    for dirpath, _, filenames in os.walk(backup_path):
        for name in filenames:
            file_path = os.path.join(dirpath, name)
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass

    return {
        "path": backup_path,
        "modified": modified,
        "size_bytes": total_size,
    }

# Format summary of existing backup
def format_existing_backup_summary(info):
    if info is None:
        return ""
    date_str = (
        time.strftime("%Y-%m-%d %#I:%M %p", time.localtime(info["modified"]))
        if info["modified"]
        else "Unknown date"
    )
    return f"Created: {date_str}  |  Size: {format_bytes(info['size_bytes'])}"

# Detect available drives
def detect_drives():
    drives = []
    system_drive = os.environ["SystemDrive"].upper()

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if not os.path.exists(drive):
            continue
        if drive[:2].upper() == system_drive:
            continue
        try:
            drive_type = win32file.GetDriveType(drive)
            if drive_type in [2, 3]:
                label = win32api.GetVolumeInformation(drive)[0]
                if not label:
                    label = "External Drive"
                drives.append((drive, label))
        except:
            pass

    return drives


def is_valid_hour(value):
    if value == "":
        return True
    if value.isdigit() and len(value) <= 2:
        return int(value) <= 12
    return False


def is_valid_minute(value):
    if value == "":
        return True
    if value.isdigit() and len(value) <= 2:
        return int(value) <= 59
    return False


def validate_access_key(value):
    value = (value or "").strip()

    if not value:
        return False, "Access Key is required."

    if len(value) != 24:
        return False, "Access Key must be exactly 24 characters."

    if len(set(value)) == 1:
        return False, "Access Key cannot consist of the same repeating character."

    return True, None


def validate_secret_key(value):
    value = (value or "").strip()

    if not re.match(r"^[A-Za-z0-9/+=]{40}$", value):
        return False, "Secret Key must be exactly 40 characters (letters, numbers, +, /, =)."

    return True, None


def validate_bucket_name(value):
    value = (value or "").strip()

    if not re.match(r"^[a-z0-9.-]{3,63}$", value):
        return False, "Bucket name must be 3–63 chars: lowercase letters, numbers, hyphens, periods only."

    if not (value[0].isalnum() and value[-1].isalnum()):
        return False, "Bucket name must start and end with a lowercase letter or number."

    if ".." in value:
        return False, "Bucket name cannot contain consecutive periods (..)."

    return True, None


# Field requirement hints (? hint)
FIELD_HINTS = {
    "access_key": [
        "· Exactly 24 characters",
    ],
    "secret_key": [
        "· Exactly 40 characters",
        "· Letters, numbers, +, /, = only",
    ],
    "bucket_name": [
        "· 3–63 characters",
        "· Lowercase letters, numbers, hyphens, periods",
        "· Must start and end with a letter or number",
        "· No consecutive periods (..)",
    ],
    "endpoint_url": [
        "· Must start with http:// or https://",
    ],
    "app_password": [
        "· Exactly 16 characters, no spaces",
        "· Gmail: myaccount.google.com → Security",
        "  → 2-Step Verification → App Passwords",
        "· Repeat previous step for both Outlook and Yahoo",
    ],
}


def validate_app_password(value):
    value = (value or "").strip()
    if not value:
        return False, "App Password is required."
    if len(value) != 16:
        return False, f"App Password must be exactly 16 characters (currently {len(value)})."
    if " " in value:
        return False, "App Password cannot contain spaces."
    return True, None


def validate_all(access_key, secret_key, bucket_name, endpoint_url,
                 storage_path, auto_backup, hour, minute):
    results = {}

    ok, msg = validate_access_key(access_key)
    results["access_key"] = (ok, msg)

    ok, msg = validate_secret_key(secret_key)
    results["secret_key"] = (ok, msg)

    ok, msg = validate_bucket_name(bucket_name)
    results["bucket_name"] = (ok, msg)

    ep = (endpoint_url or "").strip()
    import re
    if not ep:
        results["endpoint_url"] = (False, "Endpoint URL is required.")
    elif not re.fullmatch(r"https?://.+", ep):
        results["endpoint_url"] = (False, "Must start with http:// or https://")
    else:
        results["endpoint_url"] = (True, None)

    drive_ok = bool(storage_path and storage_path != "No drives found")
    results["storage"] = (drive_ok, None if drive_ok else "Select a backup drive.")

    if auto_backup:
        h_ok = str(hour).isdigit() and (1 <= int(hour) <= 12)
        m_ok = str(minute).isdigit() and (0 <= int(minute) <= 59)
        results["hour"]   = (h_ok,  None if h_ok  else "Hour must be 1–12.")
        results["minute"] = (m_ok,  None if m_ok  else "Minute must be 0–59.")
    else:
        results["hour"]   = (True, None)
        results["minute"] = (True, None)

    return results


def validate_email_fields(email_enabled, recipient, password):

    if not email_enabled:
        return 0
    errors = 0
    if not (recipient or "").strip():
        errors += 1
    pw = (password or "").strip()
    if not pw:
        errors += 1
    elif not validate_app_password(pw)[0]:
        errors += 1
    return errors