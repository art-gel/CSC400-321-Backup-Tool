import pystray, PIL.Image, threading, time
from win11toast import toast
from settings_ui import open_settings
from wbadmin_backup import run_wbadmin_backup

# Backup State
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

        # optional AWS + storage fields
        self.aws_access_key = ""
        self.aws_secret_key = ""
        self.s3_bucket_name = ""
        self.storage_path = ""


state = BackupState()

image = PIL.Image.open("backup.jpg")


# Notifications
def notify(title, message):
    toast(title, message, duration="short")


# Tray Tooltip Update
def update_icon(icon):
    icon.title = (
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

    notify("3-2-1 Backup Tool", "Backup Starting")

    source_drive = "C:" #let user choose?
    target_drive = "E:"
    returncode = run_wbadmin_backup(target_drive, source_drive)
    
    stages = ["Creating Image", "Encrypting", "Uploading to S3", "Finalizing"]

    for stage in stages:
        time.sleep(2.5)

    state.status = "Idle"

    update_icon(icon)
    if returncode == 0:
        notify("3-2-1 Backup Tool", "Backup Completed Successfully!")
        state.last_backup = time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        notify("3-2-1 Backup Tool", f"Backup failed.")


# Tray menu
def on_click(icon, item):

    if str(item) == "Exit":
        icon.stop()

    elif str(item) == "Run Backup Now":
        threading.Thread(
            target=run_backup,
            args=(icon,),
            daemon=True
        ).start()


# Create tray icon
icon = pystray.Icon(
    "BackupTool",
    image,
    menu=pystray.Menu(
        pystray.MenuItem("Run Backup Now", on_click),
        pystray.MenuItem(
            "Settings",
            lambda icon, item: threading.Thread(
                target=open_settings,
                args=(icon, state, update_icon),
                daemon=True
            ).start()
        ),
        pystray.MenuItem("View Logs", on_click),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_click)
    )
)

update_icon(icon)

def launch_settings_first():
    open_settings(icon, state, update_icon)


# This will launch the settings window on the first launch
threading.Thread(target=launch_settings_first, daemon=True).start()

icon.run()
