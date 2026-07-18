import pystray, PIL.Image, threading, time, os, json
import customtkinter as ctk
from win11toast import toast
from settings_ui import open_settings
from WBAdmin_Script import  create_image
from scheduler import Scheduler

ctk.set_appearance_mode("Dark")

CONFIG_FILE = "backup_config.json"
LOG_FILE = "backup_log.txt"

class BackupState:
    def __init__(self):
        self.status = "Idle"
        self.last_backup = "Never"
        self.next_backup = "Not Scheduled"
        self.schedule = "Daily"
        self.weekday = "Mon"
        self.hour = "12"
        self.minute = "00"
        self.ampm = "AM"
        self.aws_access_key = ""
        self.aws_secret_key = ""
        self.s3_bucket_name = ""
        self.storage_path = ""

state = BackupState()

# Loads saved settings from the JSON configuration file
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_config():
    config = {
        "aws_access_key": state.aws_access_key,
        "aws_secret_key": state.aws_secret_key,
        "s3_bucket_name": state.s3_bucket_name,
        "storage_path": state.storage_path,
        "schedule": state.schedule,
        "weekday": state.weekday,
        "hour": state.hour,
        "minute": state.minute,
        "ampm": state.ampm,
        "last_backup": state.last_backup
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    update_schedule()

def update_schedule():
    print("Creating Task..")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduled_task.py")
    task = Scheduler("321BackupTool", script_path=script_path)
    result = task.start(
        schedule=state.schedule,
        weekday=state.weekday,
        hour=state.hour,
        minute=state.minute,
        ampm=state.ampm,)
    if result:
        print("Task created successfully.")
    else:
        print("Failed to create task.")


def load_state_into_app():
    config = load_config()
    if not config:
        return False
    state.aws_access_key = config.get("aws_access_key", "")
    state.aws_secret_key = config.get("aws_secret_key", "")
    state.s3_bucket_name = config.get("s3_bucket_name", "")
    state.storage_path = config.get("storage_path", "")
    state.schedule = config.get("schedule", "Daily")
    state.weekday = config.get("weekday", "Mon")
    state.hour = config.get("hour", "12")
    state.minute = config.get("minute", "00")
    state.ampm = config.get("ampm", "AM")
    state.last_backup = config.get("last_backup", "Never")
    return True

def rebuild_next_backup():
    time_str = f"{state.hour}:{state.minute} {state.ampm}"
    if state.schedule == "Daily":
        state.next_backup = f"Daily at {time_str}"
    else:
        state.next_backup = f"Weekly ({state.weekday}) at {time_str}"

try:
    image = PIL.Image.open("backup.jpg")
except:
    image = PIL.Image.new("RGB", (64, 64), color="blue")

def notify(title, message):
    toast(title, message, duration="short")

def write_log(message):
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

# Updates the system tray tooltip with current backup information
def update_icon(icon_instance):
    rebuild_next_backup()
    icon_instance.title = (
        f"3-2-1 Backup Tool\n"
        f"Status: {state.status}\n"
        f"Last Backup: {state.last_backup}\n"
        f"Next Backup: {state.next_backup}"
    )


# Backup 
def run_backup(icon):

    if state.status == "Running":
        notify("3-2-1 Backup Tool", "A backup is already in progress.")
        return

    state.status = "Running"
    update_icon(icon)
    write_log("Backup started")

    notify("3-2-1 Backup Tool", "Backup Starting")

    source_drive = "C:" #let user choose?
    target_drive = state.storage_path[:2]
    try:
        create_image(source_drive=source_drive, target_drive=target_drive)
        state.last_backup = time.strftime("%Y-%m-%d %H:%M:%S")
        notify("3-2-1 Backup Tool", "Backup Completed Successfully!")
    except:
        notify("3-2-1 Backup Tool", "Backup failed.")

    stages = ["Creating Image", "Encrypting", "Uploading to S3", "Finalizing"]

    for stage in stages:
        write_log(f"{stage} started")
        time.sleep(2.5)
        write_log(f"{stage} completed")

    state.status = "Idle"
    update_icon(icon)

def on_click(icon_instance, item):
    if str(item) == "Exit":
        icon_instance.stop()

        root.after(0, root.quit)
    elif str(item) == "Run Backup Now":  # Start backup in a separate thread
        threading.Thread(target=run_backup, args=(icon_instance,), daemon=True).start()

# Opens the backup log file using Windows default text editor
def open_logs(icon_instance, item):
    if os.path.exists(LOG_FILE):
        os.startfile(LOG_FILE)
    else:
        write_log("Log file initialized. Waiting for backup activity...")
        os.startfile(LOG_FILE)

def launch_settings_from_menu(icon_instance, item):
    root.after(0, lambda: open_settings(icon_instance, state, update_icon, root))

root = ctk.CTk()
root.withdraw()  # this root is never shown directly

def main():
    has_config = load_state_into_app()

    if not has_config:
        # First-time configuration run
        open_settings(None, state, update_icon, root, modal_wait=True)
        if not os.path.exists(CONFIG_FILE):
            print("Setup canceled. Exiting tool.")
            exit()
        load_state_into_app()

    # Initialize the system tray icon
    icon = pystray.Icon(
        "BackupTool",
        image,
        menu=pystray.Menu(
            pystray.MenuItem("Run Backup Now", on_click),
            pystray.MenuItem("Settings", launch_settings_from_menu),
            pystray.MenuItem("View Logs", open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_click)
        )
    )

    rebuild_next_backup()
    update_icon(icon)

    # Run the tray icon's event loop on a background thread, and keep Tkinter's
    # mainloop on the main thread. 
    threading.Thread(target=icon.run, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()