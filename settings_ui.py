import customtkinter as ctk
import json, os, shutil, system_checks
from PIL import Image
from CTkToolTip import CTkToolTip
from scheduler import Scheduler


def open_settings(icon, state, update_icon, root, modal_wait=False):

    app = ctk.CTkToplevel(root)
    app.geometry("560x430")
    app.title("3-2-1 Backup Tool Settings")
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup.ico")
        app.after(200, lambda: app.iconbitmap(icon_path))
    except:
        pass
    
    app.resizable(False, False)
    app.minsize(560, 430)
    app.transient(root)
    app.grab_set()
    app.focus_force()

    def on_close():
        app.grab_release()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)

    # Tabs
    my_tab = ctk.CTkTabview(app, corner_radius=10, border_width=1)
    my_tab.pack(pady=(10, 10), padx=20, fill="both", expand=True)

    tab1 = my_tab.add("Credentials")
    tab2 = my_tab.add("Storage")
    tab3 = my_tab.add("Schedule")
    tab4 = my_tab.add("Notifications")

    # Credentials Tab — two-column grid 
    tab1.columnconfigure(0, weight=1, minsize=250)
    tab1.columnconfigure(1, weight=1, minsize=250)

    ctk.CTkLabel(tab1, text="Cloud Storage Credentials",
                 font=("Arial", 14, "bold")).grid(
        row=0, column=0, columnspan=2, pady=(16, 10))

    ENTRY_W = 220
    PAD_X   = (14, 10)
    LBL_PAD = (10, 8)

    def make_label_row(parent, text, hint_key, grid_row, grid_col,
                       colspan=1, pady=LBL_PAD):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=grid_row, column=grid_col, columnspan=colspan,
                   sticky="w", padx=(PAD_X[0], 0), pady=pady)

        ctk.CTkLabel(frame, text=text, anchor="w",
                     font=("Arial", 12)).pack(side="left")

        def show_hint():
            bx = q_btn.winfo_rootx()
            by = q_btn.winfo_rooty() + q_btn.winfo_height() + 4

            popup = ctk.CTkToplevel(app)
            popup.wm_overrideredirect(True)
            popup.geometry(f"+{bx}+{by}")
            popup.lift()
            popup.focus_force()

            popup_frame = ctk.CTkFrame(
                popup, corner_radius=8, border_width=2,
                border_color="#e0533b",
                fg_color=("#2b1a1a", "#2b1a1a"))
            popup_frame.pack(padx=0, pady=0)

            ctk.CTkLabel(popup_frame,
                         text=f"  {text} requirements",
                         font=("Arial", 11, "bold"),
                         text_color="#e0533b").pack(anchor="w", padx=12, pady=(8, 2))

            for line in system_checks.FIELD_HINTS[hint_key]:
                ctk.CTkLabel(popup_frame, text=line, anchor="w",
                             font=("Arial", 11),
                             text_color=("gray90", "gray90"),
                             justify="left").pack(anchor="w", padx=12, pady=(2, 0))

            ctk.CTkLabel(popup_frame, text="").pack(pady=4)

            popup.bind("<FocusOut>", lambda e: popup.destroy())
            popup.bind("<Escape>",   lambda e: popup.destroy())

        q_btn = ctk.CTkButton(frame, text="?", width=22, height=22,
                              font=("Arial", 11, "bold"),
                              fg_color="#3d1a1a",
                              text_color="#e0533b",
                              hover_color="#5a2020",
                              corner_radius=11,
                              command=show_hint)
        q_btn.pack(side="left", padx=(6, 0))
        q_btn.pack_forget()
        return q_btn

    q_bucket = make_label_row(tab1, "Bucket Name", "bucket_name", 1, 0)
    bucket = ctk.CTkEntry(tab1, width=ENTRY_W)
    bucket.insert(0, getattr(state, "s3_bucket_name", ""))
    bucket.grid(row=2, column=0, padx=PAD_X, sticky="w")

    q_access_key = make_label_row(tab1, "Access Key", "access_key", 3, 0)
    s3_key = ctk.CTkEntry(tab1, width=ENTRY_W)
    s3_key.insert(0, getattr(state, "s3_access_key", ""))
    s3_key.grid(row=4, column=0, padx=PAD_X, sticky="w")

    ctk.CTkLabel(tab1, text="Region", anchor="w",
                 font=("Arial", 12)).grid(
        row=1, column=1, sticky="w", padx=PAD_X, pady=LBL_PAD)

 
    AWS_REGIONS = [
        "us-east-1",      "us-east-2",
        "us-west-1",      "us-west-2",
        "af-south-1",
        "ap-east-1",      "ap-south-1",      "ap-south-2",
        "ap-northeast-1", "ap-northeast-2",  "ap-northeast-3",
        "ap-southeast-1", "ap-southeast-2",  "ap-southeast-3", "ap-southeast-4",
        "ca-central-1",   "ca-west-1",
        "eu-central-1",   "eu-central-2",
        "eu-west-1",      "eu-west-2",       "eu-west-3",
        "eu-north-1",     "eu-south-1",      "eu-south-2",
        "il-central-1",
        "me-central-1",   "me-south-1",
        "sa-east-1",
    ]
    saved_region = getattr(state, "s3_region", "")
    region_var   = ctk.StringVar(
        value=saved_region if saved_region in AWS_REGIONS else AWS_REGIONS[0])
    region_menu  = ctk.CTkOptionMenu(tab1, variable=region_var,
                                     values=AWS_REGIONS, width=160)
    region_menu.grid(row=2, column=1, padx=PAD_X, sticky="w")

    q_endpoint = make_label_row(tab1, "Endpoint URL", "endpoint_url", 3, 1)
    endpoint_entry = ctk.CTkEntry(tab1, width=ENTRY_W)
    endpoint_entry.insert(0, getattr(state, "s3_endpoint_url", ""))
    endpoint_entry.grid(row=4, column=1, padx=PAD_X, sticky="w")

    # Secret Key
    q_secret = make_label_row(tab1, "Secret Key", "secret_key",
                              grid_row=5, grid_col=0, colspan=2, pady=(12, 0))
    secret_frame = ctk.CTkFrame(tab1, fg_color="transparent")
    secret_frame.grid(row=6, column=0, columnspan=2, padx=PAD_X, sticky="w")

    s3_secret = ctk.CTkEntry(secret_frame, width=ENTRY_W * 2 - 10, show="*")
    s3_secret.insert(0, getattr(state, "s3_secret_key", ""))
    s3_secret.pack(side="left")

    secret_visible = False
    eye_open   = ctk.CTkImage(Image.open("visibility_on.png"),  size=(20, 20))
    eye_closed = ctk.CTkImage(Image.open("visibility_off.png"), size=(20, 20))

    def toggle_secret():
        nonlocal secret_visible
        if secret_visible:
            s3_secret.configure(show="*")
            eye_btn.configure(image=eye_closed)
        else:
            s3_secret.configure(show="")
            eye_btn.configure(image=eye_open)
        secret_visible = not secret_visible

    eye_btn = ctk.CTkButton(
        secret_frame, text="", image=eye_closed, width=36,
        fg_color="transparent", hover_color=("gray80", "gray30"),
        command=toggle_secret)
    eye_btn.pack(side="left", padx=(4, 0))

    # Storage Tab
    storage_path = ctk.StringVar(value=getattr(state, "storage_path", ""))
    drive_map = {}

    storage_frame = ctk.CTkFrame(tab2)
    storage_frame.pack(pady=15, padx=20, fill="both", expand=True)

    ctk.CTkLabel(storage_frame, text="Backup Storage Location",
                 font=("Arial", 14, "bold")).pack(pady=(16, 10))

    stats_label = ctk.CTkLabel(storage_frame, text="", font=("Arial", 14))

    existing_backup_found = {"value": False}
    state.replace_existing_backup = False

    existing_backup_label = ctk.CTkLabel(
        storage_frame, text="", font=("Arial", 14),
        text_color="#e0a030", wraplength=380, justify="left")

    def update_stats():
        selected = storage_path.get()
        drive = drive_map.get(selected)

        existing_backup_label.pack_forget()
        existing_backup_found["value"] = False
        state.replace_existing_backup = False

        if not drive:
            stats_label.configure(text="Please connect an external backup drive")
            return

        total, used, free = shutil.disk_usage(drive)
        stats_label.configure(
            text=(f"Total Capacity: {system_checks.format_bytes(total)}\n"
                  f"Free Space: {system_checks.format_bytes(free)}\n"))

        existing = system_checks.find_existing_backup(drive)
        if existing:
            summary = system_checks.format_existing_backup_summary(existing)
            existing_backup_label.configure(
                text=(f"This drive already has a backup.\n{summary}\n\n"
                      f"Replace it or select a different drive."))
            existing_backup_label.pack(pady=(5, 10))
            existing_backup_found["value"] = True

    def load_drives():
        drive_map.clear()
        detected = system_checks.detect_drives()
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
        drive_frame, variable=storage_path, values=[], width=220,
        command=lambda choice: update_stats())
    drive_menu.pack(side="left", padx=(0, 5))

    refresh_image = ctk.CTkImage(Image.open("refresh.png"), size=(20, 20))
    refresh_btn = ctk.CTkButton(
        drive_frame, text="", image=refresh_image, width=40, height=35,
        fg_color="transparent", hover_color=("gray80", "gray30"),
        command=load_drives)
    refresh_btn.pack(side="left")

    CTkToolTip(refresh_btn, message="Scan Drives",
               bg_color="gray30", text_color="white")

    stats_label.pack(pady=10)
    app.after(100, load_drives)

    # Schedule Tab
    def validate_hour(P):   return system_checks.is_valid_hour(P)
    def validate_minute(P): return system_checks.is_valid_minute(P)

    v_hour   = app.register(validate_hour)
    v_minute = app.register(validate_minute)

    schedule_var = ctk.StringVar(app, value=state.schedule)
    weekday_var  = ctk.StringVar(app, value=state.weekday)
    ampm_var     = ctk.StringVar(app, value=state.ampm)

    ctk.CTkLabel(tab3, text="Backup Schedule",
                 font=("Arial", 14, "bold")).pack(pady=(16, 10))
    schedule_menu = ctk.CTkOptionMenu(
        tab3, variable=schedule_var, values=["Daily", "Weekly"])
    schedule_menu.pack(pady=8)

    day_label    = ctk.CTkLabel(tab3, text="Day")
    weekday_menu = ctk.CTkOptionMenu(
        tab3, variable=weekday_var,
        values=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

    def toggle_weekday(*args):
        if schedule_var.get() == "Weekly":
            day_label.pack(pady=(8, 0))
            weekday_menu.pack(pady=5)
        else:
            day_label.pack_forget()
            weekday_menu.pack_forget()

    schedule_menu.configure(command=lambda choice: toggle_weekday())
    toggle_weekday()

    ctk.CTkLabel(tab3, text="Time").pack(pady=(10, 8))
    time_frame = ctk.CTkFrame(tab3, fg_color="transparent")
    time_frame.pack(pady=5)

    hour_entry = ctk.CTkEntry(
        time_frame, width=50,
        validate="key", validatecommand=(v_hour, "%P"))
    hour_entry.insert(0, "")
    hour_entry.insert(0, str(state.hour).lstrip("0"))
    hour_entry.pack(side="left", padx=2)

    ctk.CTkLabel(time_frame, text=":", font=("Arial", 14, "bold")).pack(side="left", padx=2)

    minute_entry = ctk.CTkEntry(
        time_frame, width=50,
        validate="key", validatecommand=(v_minute, "%P"))
    minute_entry.insert(0, "")
    minute_entry.insert(0, str(state.minute).zfill(2))
    minute_entry.pack(side="left", padx=2)

    ampm_menu = ctk.CTkOptionMenu(
        time_frame, variable=ampm_var, values=["AM", "PM"], width=75)
    ampm_menu.pack(side="left", padx=5)

    auto_backup_var = ctk.BooleanVar(value=getattr(state, "auto_backup", True))

    def on_toggle_switch():
        enabled = auto_backup_var.get()
        if enabled:
            toggle_switch.configure(text="Automatic")
            schedule_menu.configure(state="normal")
            hour_entry.configure(state="normal")
            minute_entry.configure(state="normal")
            ampm_menu.configure(state="normal")
            if schedule_var.get() == "Weekly":
                weekday_menu.configure(state="normal")
        else:
            toggle_switch.configure(text="Manual")
            schedule_menu.configure(state="disabled")
            hour_entry.configure(state="disabled")
            minute_entry.configure(state="disabled")
            ampm_menu.configure(state="disabled")
            weekday_menu.configure(state="disabled")

    toggle_switch = ctk.CTkSwitch(
        tab3, text="Automatic",
        variable=auto_backup_var,
        command=on_toggle_switch)
    toggle_switch.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    # Apply the saved toggle state on open
    on_toggle_switch()

    storage_frame.pack(pady=(5, 15), padx=20, fill="both", expand=True)

    # Validation
    def check_all_fields(*_):
        results = system_checks.validate_all(
            access_key   = s3_key.get().strip(),
            secret_key   = s3_secret.get().strip(),
            bucket_name  = bucket.get().strip(),
            endpoint_url = endpoint_entry.get().strip(),
            storage_path = storage_path.get(),
            auto_backup  = auto_backup_var.get(),
            hour         = hour_entry.get().strip(),
            minute       = minute_entry.get().strip(),
        )

        def _toggle_q(q_btn, field_key, current_value):
            ok, _ = results[field_key]
            if not ok and current_value.strip():
                q_btn.pack(side="left", padx=(6, 0))
            else:
                q_btn.pack_forget()

        _toggle_q(q_access_key, "access_key",  s3_key.get())
        _toggle_q(q_secret,     "secret_key",  s3_secret.get())
        _toggle_q(q_bucket,     "bucket_name", bucket.get())
        _toggle_q(q_endpoint,   "endpoint_url", endpoint_entry.get())

        errors = sum(1 for ok, _ in results.values() if not ok)

        # Add email validation if notifications enabled
        try:
            errors += system_checks.validate_email_fields(
                email_enabled = email_enabled_var.get(),
                recipient     = email_recipient.get().strip(),
                password      = email_password.get().strip(),
            )
        except NameError:
            pass  # emails are not yet defined on first call

        if errors == 0:
            save_btn.configure(state="normal",
                               fg_color=("#1f6aa5", "#1f6aa5"),
                               text_color="white")
        else:
            save_btn.configure(state="disabled",
                               fg_color=("gray70", "gray40"),
                               text_color=("gray50", "gray60"))

    for entry in (s3_key, s3_secret, bucket, endpoint_entry,
                  hour_entry, minute_entry):
        entry.bind("<KeyRelease>", check_all_fields)

    storage_path.trace_add("write", check_all_fields)
    auto_backup_var.trace_add("write", check_all_fields)

    # Notifications Tab — two-column grid
    email_enabled_var = ctk.BooleanVar(value=getattr(state, "email_enabled", False))

    tab4.columnconfigure(0, weight=1, minsize=250)
    tab4.columnconfigure(1, weight=1, minsize=250)

    ctk.CTkLabel(tab4, text="Email Notifications",
                 font=("Arial", 14, "bold")).grid(
        row=0, column=0, columnspan=2, pady=(16, 6))

    email_toggle = ctk.CTkSwitch(tab4, text="Off",
                                 variable=email_enabled_var,
                                 command=lambda: toggle_email_fields())
    email_toggle.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    EPAD_X = (14, 8)
    ELBPAD  = (8, 0)
    ENTRY_E = 220

    # Left column
    ctk.CTkLabel(tab4, text="Email Address", anchor="w",
                 font=("Arial", 12)).grid(
        row=1, column=0, sticky="w", padx=EPAD_X, pady=ELBPAD)
    email_recipient = ctk.CTkEntry(tab4, width=ENTRY_E,
                                   placeholder_text="you@gmail.com")
    email_recipient.insert(0, getattr(state, "email_recipient", ""))
    email_recipient.grid(row=2, column=0, padx=EPAD_X, sticky="w")

    app_pass_lbl_frame = ctk.CTkFrame(tab4, fg_color="transparent")
    app_pass_lbl_frame.grid(row=3, column=0, sticky="w", padx=(EPAD_X[0], 0), pady=ELBPAD)
    ctk.CTkLabel(app_pass_lbl_frame, text="App Password", anchor="w",
                 font=("Arial", 12)).pack(side="left")

    def show_app_pass_hint():
        bx = app_pass_q.winfo_rootx()
        by = app_pass_q.winfo_rooty() + app_pass_q.winfo_height() + 4
        popup = ctk.CTkToplevel(app)
        popup.wm_overrideredirect(True)
        popup.geometry(f"+{bx}+{by}")
        popup.lift()
        popup.focus_force()
        pf = ctk.CTkFrame(popup, corner_radius=8, border_width=2,
                          border_color="#e0533b", fg_color=("#2b1a1a", "#2b1a1a"))
        pf.pack(padx=0, pady=0)
        ctk.CTkLabel(pf, text="  App Password requirements",
                     font=("Arial", 11, "bold"),
                     text_color="#e0533b").pack(anchor="w", padx=12, pady=(8, 2))
        for line in system_checks.FIELD_HINTS["app_password"]:
            ctk.CTkLabel(pf, text=line, anchor="w", font=("Arial", 11),
                         text_color=("gray90", "gray90"),
                         justify="left").pack(anchor="w", padx=12, pady=(2, 0))
        ctk.CTkLabel(pf, text="").pack(pady=4)
        popup.bind("<FocusOut>", lambda e: popup.destroy())
        popup.bind("<Escape>",   lambda e: popup.destroy())

    app_pass_q = ctk.CTkButton(app_pass_lbl_frame, text="?", width=22, height=22,
                               font=("Arial", 11, "bold"),
                               fg_color="#3d1a1a", text_color="#e0533b",
                               hover_color="#5a2020", corner_radius=11,
                               command=show_app_pass_hint)
    app_pass_q.pack(side="left", padx=(6, 0))
    app_pass_q.pack_forget()

    email_pass_frame = ctk.CTkFrame(tab4, fg_color="transparent")
    email_pass_frame.grid(row=4, column=0, padx=EPAD_X, sticky="w")

    email_password = ctk.CTkEntry(email_pass_frame, width=ENTRY_E - 42, show="*",
                                  placeholder_text="16-char app password")
    email_password.insert(0, getattr(state, "email_password", ""))
    email_password.pack(side="left")

    email_pass_visible = False
    def toggle_email_pass():
        nonlocal email_pass_visible
        if email_pass_visible:
            email_password.configure(show="*")
            ep_eye_btn.configure(image=eye_closed)
        else:
            email_password.configure(show="")
            ep_eye_btn.configure(image=eye_open)
        email_pass_visible = not email_pass_visible

    ep_eye_btn = ctk.CTkButton(email_pass_frame, text="", image=eye_closed,
                               width=36, fg_color="transparent",
                               hover_color=("gray80", "gray30"),
                               command=toggle_email_pass)
    ep_eye_btn.pack(side="left", padx=(4, 0))

    ctk.CTkLabel(tab4, text="  Gmail/Outlook require an App Password.",
                 font=("Arial", 10), text_color="gray60").grid(
        row=6, column=0, sticky="w", padx=EPAD_X, pady=(2, 0))

    # Validate app password — show ? if filled but wrong length
    def validate_email_fields(*_):
        pw = email_password.get().strip()
        if pw:
            ok, _ = system_checks.validate_app_password(pw)
            if not ok:
                app_pass_q.pack(side="left", padx=(6, 0))
            else:
                app_pass_q.pack_forget()
        else:
            app_pass_q.pack_forget()

    email_password.bind("<KeyRelease>", validate_email_fields)

    # Notify me checkboxes 
    ctk.CTkLabel(tab4, text="Notify me when:", anchor="w",
                 font=("Arial", 12)).grid(
        row=1, column=1, sticky="w", padx=EPAD_X, pady=ELBPAD)

    notify_success_var = ctk.BooleanVar(value=getattr(state, "notify_on_success", True))
    notify_failure_var = ctk.BooleanVar(value=getattr(state, "notify_on_failure", True))
    notify_missed_var  = ctk.BooleanVar(value=getattr(state, "notify_on_missed",  True))

    ctk.CTkCheckBox(tab4, text="Backup succeeded",
                    variable=notify_success_var).grid(
        row=2, column=1, sticky="w", padx=EPAD_X, pady=(4, 0))
    ctk.CTkCheckBox(tab4, text="Backup failed",
                    variable=notify_failure_var).grid(
        row=3, column=1, sticky="w", padx=EPAD_X, pady=(4, 0))
    ctk.CTkCheckBox(tab4, text="Missed backup ran on startup",
                    variable=notify_missed_var).grid(
        row=4, column=1, sticky="w", padx=EPAD_X, pady=(4, 0))

    def toggle_email_fields():
        enabled = email_enabled_var.get()
        state_str = "normal" if enabled else "disabled"
        email_toggle.configure(text="Automatic" if enabled else "Off")
        for w in (email_recipient, email_password, ep_eye_btn):
            try:
                w.configure(state=state_str)
            except Exception:
                pass

    # Apply initial state
    toggle_email_fields()

    # Re-run save button check when email fields change
    def recheck_save(*_):
        email_errors = system_checks.validate_email_fields(
            email_enabled  = email_enabled_var.get(),
            recipient      = email_recipient.get().strip(),
            password       = email_password.get().strip(),
        )
        # Read current save button state from check_all_fields result
        # by calling it directly
        check_all_fields()

    for entry in (email_recipient, email_password):
        entry.bind("<KeyRelease>", lambda e: recheck_save())
    email_enabled_var.trace_add("write", lambda *_: recheck_save())



    # Save Settings
    def save_settings():
        ep_val = endpoint_entry.get().strip()

        state.replace_existing_backup = existing_backup_found["value"]

        state.schedule        = schedule_var.get()
        state.weekday         = weekday_var.get()
        state.hour            = hour_entry.get().strip().lstrip("0") or "12"
        state.minute          = minute_entry.get().zfill(2)
        state.ampm            = ampm_var.get()
        state.auto_backup     = auto_backup_var.get()

        state.s3_access_key   = s3_key.get()
        state.s3_secret_key   = s3_secret.get()
        state.s3_bucket_name  = bucket.get()
        state.s3_region       = region_var.get()
        state.s3_endpoint_url = ep_val
        state.storage_path    = storage_path.get()

        state.email_enabled      = email_enabled_var.get()
        state.email_recipient    = email_recipient.get().strip()
        state.email_sender       = email_recipient.get().strip()
        state.email_password     = email_password.get().strip()
        state.notify_on_success  = notify_success_var.get()
        state.notify_on_failure  = notify_failure_var.get()
        state.notify_on_missed   = notify_missed_var.get()

        config_data = {
            "s3_access_key":   state.s3_access_key,
            "s3_secret_key":   state.s3_secret_key,
            "s3_bucket_name":  state.s3_bucket_name,
            "s3_region":       state.s3_region,
            "s3_endpoint_url": state.s3_endpoint_url,
            "storage_path":    state.storage_path,
            "schedule":        state.schedule,
            "weekday":         state.weekday,
            "hour":            state.hour,
            "minute":          state.minute,
            "ampm":            state.ampm,
            "auto_backup":        state.auto_backup,
            "last_backup":        state.last_backup,
            "email_enabled":      state.email_enabled,
            "email_recipient":    state.email_recipient,
            "email_sender":       state.email_sender,
            "email_password":     state.email_password,
            "notify_on_success":  state.notify_on_success,
            "notify_on_failure":  state.notify_on_failure,
            "notify_on_missed":   state.notify_on_missed,
        }

        if auto_backup_var.get():
            print("Creating Task…")
            script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "scheduled_task.py")
            task = Scheduler("321BackupTool", script_path=script_path)
            result = task.start(
                schedule=state.schedule,
                weekday=state.weekday,
                hour=state.hour,
                minute=state.minute,
                ampm=state.ampm)
            print("Task created successfully." if result else "Failed to create task.")

        with open("backup_config.json", "w") as f:
            json.dump(config_data, f, indent=4)

        if icon is not None:
            update_icon(icon)

        on_close()

    save_btn = ctk.CTkButton(app, text="Save", command=save_settings,
                             state="disabled",
                             fg_color=("gray70", "gray40"),
                             text_color=("gray50", "gray60"))
    save_btn.pack(pady=(0, 15))

    app.after(200, check_all_fields)

    if modal_wait:
        root.wait_window(app)