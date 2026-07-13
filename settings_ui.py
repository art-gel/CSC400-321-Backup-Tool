import customtkinter as ctk
import json, os, shutil, win32api, win32file
from tkinter import messagebox
from PIL import Image
from CTkToolTip import CTkToolTip

def open_settings(icon, state, update_icon, root, modal_wait=False):

    # Use a CTkToplevel of the single persistent root instead of a second
    # ctk.CTk() instance. Multiple CTk() roots is what caused the
    # "main thread is not in main loop" / "invalid command name ... after
    # script" errors and the laggy tab switching.
    app = ctk.CTkToplevel(root)
    app.geometry("500x420")
    app.title("3-2-1 Backup Tool Settings")
    try:
        app.iconbitmap("backup.ico")
    except:
        pass
    app.resizable(False, False)

    # Make it behave like a modal dialog
    app.transient(root)
    app.grab_set()
    app.focus_force()

    def on_close():
        app.grab_release()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    # Tabs
    my_tab = ctk.CTkTabview(app, width=460, height=320, corner_radius=10, border_width=1)
    my_tab.pack(pady=(10, 10), padx=20, fill="both", expand=True)

    tab1 = my_tab.add("AWS Setup")
    tab2 = my_tab.add("Storage")
    tab3 = my_tab.add("Backup Schedule")

    # AWS Setup Tab
    ctk.CTkLabel(tab1, text="AWS Credentials", font=("Arial", 14, "bold")).pack(pady=10)
    ctk.CTkLabel(tab1, text="AWS Access Key").pack(anchor="w", padx=20)
    aws_key = ctk.CTkEntry(tab1, width=350)
    aws_key.insert(0, getattr(state, "aws_access_key", ""))
    aws_key.pack(pady=(0, 10))

    ctk.CTkLabel(tab1, text="AWS Secret Access Key").pack(anchor="w", padx=20)
    aws_secret = ctk.CTkEntry(tab1, width=350, show="*")
    aws_secret.insert(0, getattr(state, "aws_secret_key", ""))
    aws_secret.pack(pady=(0, 10))

    ctk.CTkLabel(tab1, text="S3 Bucket Name").pack(anchor="w", padx=20)
    bucket = ctk.CTkEntry(tab1, width=350)
    bucket.insert(0, getattr(state, "s3_bucket_name", ""))
    bucket.pack()

    # Storage Tab
    storage_path = ctk.StringVar(value=getattr(state, "storage_path", ""))
    drive_map = {}

    storage_frame = ctk.CTkFrame(tab2)
    storage_frame.pack(pady=15, padx=20, fill="both", expand=True)

    ctk.CTkLabel(storage_frame, text="Backup Storage Location",
                 font=("Arial", 14, "bold")).pack(pady=10)

    stats_label = ctk.CTkLabel(storage_frame, text="", font=("Arial", 14))

    def detect_drives():
        drives = []
        system_drive = os.environ["SystemDrive"].upper()

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if not os.path.exists(drive):
                continue
            # Ignores the Windows system drive
            if drive[:2].upper() == system_drive:
                continue
            try:
                drive_type = win32file.GetDriveType(drive)
                # Removable USB + external fixed drives
                if drive_type in [2, 3]:
                    label = win32api.GetVolumeInformation(drive)[0]
                    if not label:
                        label = "External Drive"
                    drives.append((drive, label))

            except:
                pass

        return drives

    def format_storage(size):
        gb = size / (1024**3)
        if gb >= 1024:
            return f"{gb / 1024:.2f} TB"
        else:
            return f"{gb:.2f} GB"

    def update_stats():
        selected = storage_path.get()
        drive = drive_map.get(selected)

        if not drive:
            stats_label.configure(text="Please connect an external backup drive")
            return

        total, used, free = shutil.disk_usage(drive)

        stats_label.configure(
            text=(
                f"Total Capacity: {format_storage(total)}\n"
                f"Free Space: {format_storage(free)}\n"
            )
        )

    # Scans connected drives again when the refresh button is clicked
    def load_drives():
        drive_map.clear()
        detected = detect_drives()
        values = []
        for path, label in detected:
            display_name = f"{path[:2]} - {label}"
            drive_map[display_name] = path
            values.append(display_name)
        if not values:
            values = ["No drives found"]
            storage_path.set(values[0])
            stats_label.configure(text="Please connect an external backup drive")
        else:
            drive_menu.configure(values=values)
            storage_path.set(values[0])
            update_stats()

    drive_frame = ctk.CTkFrame(storage_frame)
    drive_frame.pack(pady=5)

    drive_menu = ctk.CTkOptionMenu(
        drive_frame,
        variable=storage_path,
        values=[],
        width=220,
        command=lambda choice: update_stats()
    )
    drive_menu.pack(side="left", padx=(0, 5))

    refresh_image = ctk.CTkImage(
        Image.open("refresh.png"),
        size=(20, 20)
    )
    refresh_btn = ctk.CTkButton(
        drive_frame,
        text="",
        image=refresh_image,
        width=40,
        height=35,
        fg_color="transparent",
        hover_color=("gray80", "gray30"),
        command=load_drives
    )
    refresh_btn.pack(side="left")

    tooltip = CTkToolTip(refresh_btn, message="Scan Drives",
                          bg_color="gray30", text_color="white")

    stats_label.pack(pady=10)

    app.after(100, load_drives)

    def validate_hour(P):
        # Allow empty while editing
        if P == "":
            return True

        # Allow only 1-2 digits
        if P.isdigit() and len(P) <= 2:
            return int(P) <= 12

        return False

    def validate_minute(P):
        # Allow empty while editing
        if P == "":
            return True

        # Allow only 1-2 digits
        if P.isdigit() and len(P) <= 2:
            return int(P) <= 59

        return False

    # Register these validation rules with Tkinter
    v_hour = app.register(validate_hour)
    v_minute = app.register(validate_minute)

    # Schedule Tab
    schedule_var = ctk.StringVar(app, value=state.schedule)
    weekday_var = ctk.StringVar(app, value=state.weekday)
    ampm_var = ctk.StringVar(app, value=state.ampm)

    ctk.CTkLabel(tab3, text="Schedule Type", font=("Arial", 14, "bold")).pack(pady=10)
    schedule_menu = ctk.CTkOptionMenu(tab3, variable=schedule_var, values=["Daily", "Weekly"])
    schedule_menu.pack(pady=5)

    day_label = ctk.CTkLabel(tab3, text="Day")

    weekday_menu = ctk.CTkOptionMenu(
        tab3, variable=weekday_var, values=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    def toggle_weekday(*args):
        if schedule_var.get() == "Weekly":
            day_label.pack(pady=(5, 0))
            weekday_menu.pack(pady=5)
        else:
            day_label.pack_forget()
            weekday_menu.pack_forget()

    schedule_menu.configure(command=lambda choice: toggle_weekday())
    toggle_weekday()

    ctk.CTkLabel(tab3, text="Time").pack(pady=(10, 5))
    time_frame = ctk.CTkFrame(tab3, fg_color="transparent")  # Transparent frame matches tab perfectly
    time_frame.pack(pady=5)

    hour_entry = ctk.CTkEntry(
        time_frame,
        width=50,
        validate="key",
        validatecommand=(v_hour, "%P")
    )
    hour_entry.insert(0, "")
    hour_entry.insert(0, str(state.hour).lstrip("0"))
    hour_entry.pack(side="left", padx=2)

    ctk.CTkLabel(time_frame, text=":", font=("Arial", 14, "bold")).pack(side="left", padx=2)

    minute_entry = ctk.CTkEntry(
        time_frame,
        width=50,
        validate="key",
        validatecommand=(v_minute, "%P")
    )
    minute_entry.insert(0, "")
    minute_entry.insert(0, str(state.minute).zfill(2))
    minute_entry.pack(side="left", padx=2)

    ampm_menu = ctk.CTkOptionMenu(
        time_frame,
        variable=ampm_var,
        values=["AM", "PM"],
        width=75
    )
    ampm_menu.pack(side="left", padx=5)

    # Save Settings
    def save_settings():

        h_text = hour_entry.get().strip()
        m_text = minute_entry.get().strip()

        # Validate hour and minute
        if not h_text.isdigit() or not (1 <= int(h_text) <= 12):
            messagebox.showerror(title="Invalid Hour", message="Please enter a valid hour (1-12).")
            return

        if not m_text.isdigit() or not (0 <= int(m_text) <= 59):
            messagebox.showerror(title="Invalid Minute", message="Please enter a valid minute (0-59).")
            return

        if (
            not aws_key.get().strip()
            or not aws_secret.get().strip()
            or not bucket.get().strip()
            or storage_path.get() == "No drives found"
            or not storage_path.get().strip()
            or schedule_var.get() == ""
            or (schedule_var.get() == "Weekly" and not weekday_var.get().strip())
        ):
            messagebox.showerror(title="Incomplete Setup!",
                                  message="Please complete all required fields before saving.")
            return

        state.schedule = schedule_var.get()
        state.weekday = weekday_var.get()
        state.hour = hour_entry.get().zfill(2)
        state.minute = minute_entry.get().zfill(2)
        state.ampm = ampm_var.get()

        state.aws_access_key = aws_key.get()
        state.aws_secret_key = aws_secret.get()
        state.s3_bucket_name = bucket.get()
        state.storage_path = storage_path.get()

        # Save config instantly to JSON file
        config_data = {
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
        with open("backup_config.json", "w") as f:
            json.dump(config_data, f, indent=4)

        if icon is not None:
            update_icon(icon)

        on_close()

    save_btn = ctk.CTkButton(app, text="Save Settings", command=save_settings)
    save_btn.pack(pady=(0, 15))

    if modal_wait:
        # Only needed for the very first run, called before root.mainloop()
        # has started. wait_window() runs its own local event loop and
        # returns once `app` is destroyed - it does NOT require (or create)
        # a second Tk root, unlike the old app.mainloop() approach.
        root.wait_window(app)