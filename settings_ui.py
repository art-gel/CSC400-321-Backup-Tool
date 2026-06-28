import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("Dark")

def open_settings(icon, state, update_icon):

    app = ctk.CTk()
    app.geometry("500x400")
    app.title("3-2-1 Backup Tool Settings")
    app.iconbitmap("backup.ico")
    app.resizable(False, False)

    # Tabs
    my_tab = ctk.CTkTabview(
        app,
        width=460,
        height=320,
        corner_radius=10,
        border_width=1
    )

    my_tab.pack(pady=(10, 10), padx=20, fill="both", expand=True)

    tab1 = my_tab.add("AWS Setup")
    tab2 = my_tab.add("Storage")
    tab3 = my_tab.add("Backup Schedule")

    # AWS Setup Tab
    ctk.CTkLabel(tab1, text="AWS Credentials", font=("Arial", 14)).pack(pady=10)

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

    storage_frame = ctk.CTkFrame(tab2)
    storage_frame.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(
        storage_frame,
        text="External SSD Storage",
        font=("Arial", 14)
    ).pack(pady=(5, 5))

    ctk.CTkLabel(
        storage_frame,
        text="Select a Backup Location"
    ).pack(anchor="w", pady=(10, 5))

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            storage_path.set(folder)

    input_frame = ctk.CTkFrame(storage_frame)
    input_frame.pack(fill="x", pady=(0, 10))

    path_entry = ctk.CTkEntry(
        input_frame,
        textvariable=storage_path,
        width=300
    )
    path_entry.pack(side="left", padx=(0, 5))

    browse_btn = ctk.CTkButton(
        input_frame,
        text="Browse",
        command=browse_folder,
        width=80
    )
    browse_btn.pack(side="left")

    # Schedule Tab
    schedule_var = ctk.StringVar(value=state.schedule)
    weekday_var = ctk.StringVar(value=state.weekday)
    hour_var = ctk.StringVar(value=state.hour)
    minute_var = ctk.StringVar(value=state.minute)
    ampm_var = ctk.StringVar(value=state.ampm)

    ctk.CTkLabel(tab3, text="Schedule Type", font=("Arial", 14)).pack(pady=10)

    schedule_menu = ctk.CTkOptionMenu(
        tab3,
        variable=schedule_var,
        values=["Daily", "Weekly"]
    )
    schedule_menu.pack(pady=5)

    day_label = ctk.CTkLabel(tab3, text="Day")

    weekday_menu = ctk.CTkOptionMenu(
        tab3,
        variable=weekday_var,
        values=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    def toggle_weekday(*args):
        if schedule_var.get() == "Weekly":
            day_label.pack(pady=(10, 0))
            weekday_menu.pack(pady=5)
        else:
            day_label.pack_forget()
            weekday_menu.pack_forget()

    schedule_var.trace_add("write", toggle_weekday)
    toggle_weekday()

    ctk.CTkLabel(tab3, text="Time").pack(pady=(10, 5))

    time_frame = ctk.CTkFrame(tab3)
    time_frame.pack(pady=5)

    ctk.CTkEntry(time_frame, textvariable=hour_var, width=50).pack(side="left", padx=2)
    ctk.CTkLabel(time_frame, text=":").pack(side="left")
    ctk.CTkEntry(time_frame, textvariable=minute_var, width=50).pack(side="left", padx=2)

    ctk.CTkOptionMenu(
        time_frame,
        variable=ampm_var,
        values=["AM", "PM"],
        width=80
    ).pack(side="left", padx=5)

    # Save Settings
    def save_settings():

        state.schedule = schedule_var.get()
        state.weekday = weekday_var.get()
        state.hour = hour_var.get()
        state.minute = minute_var.get()
        state.ampm = ampm_var.get()

        state.aws_access_key = aws_key.get()
        state.aws_secret_key = aws_secret.get()
        state.s3_bucket_name = bucket.get()
        state.storage_path = storage_path.get()

        time_str = f"{state.hour}:{state.minute} {state.ampm}"

        if state.schedule == "Daily":
            state.next_backup = f"Daily at {time_str}"
        else:
            state.next_backup = f"Weekly ({state.weekday}) at {time_str}"

        update_icon(icon)
        app.destroy()

    save_btn = ctk.CTkButton(app, text="Save", command=save_settings)
    save_btn.pack(pady=(0, 15))

    app.mainloop()