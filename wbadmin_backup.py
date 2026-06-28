import subprocess
import sys
import shutil

def run_wbadmin_backup(target_drive, include_volumes):
    """
    Run a wbadmin backup.
    target_drive: e.g. "E:" or "\\\\server\\share"
    include_volumes: e.g. "C:" or "C:,E:"
    """
    cmd = [
        "wbadmin", "start", "backup",
        f"-backupTarget:{target_drive}",
        f"-include:{include_volumes}",
        "-allCritical",   # include all volumes needed to restore the OS (boot, system, etc.)
        "-quiet"
    ]

    print("Running:", " ".join(cmd))

    # Use Popen instead of subprocess.run so we can read output as it's
    # produced, rather than waiting for the process to finish and getting
    # everything back as one blob via capture_output.
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,      # capture stdout so we can read it ourselves
        stderr=subprocess.STDOUT,    # merge stderr into stdout (single stream, single loop)
        text=True,                   # decode bytes to str automatically
        bufsize=1                    # line-buffered
    )

    # Read and print output line by line as wbadmin produces it.
    # This loop blocks on each line until wbadmin writes one, but doesn't
    # wait for the whole process to finish.
    for line in process.stdout:
        print(line, end="", flush=True)  # end="" avoids double newlines; flush ensures immediate display

    # Wait for the process to fully exit and get its return code.
    process.wait()
    return process.returncode

if __name__ == "__main__":
    # Example: back up C: to E:
    target = "E:"
    volumes = "C:"

    # wbadmin is a Windows-only tool, so bail out on other platforms.
    if not sys.platform.startswith("win"):
        print("This script must be run on Windows.")
        sys.exit(1)
        
    
    returncode = run_wbadmin_backup(target, volumes)

    if returncode == 0:
        print("Backup completed successfully.")
    else:
        print(f"Backup failed with exit code {returncode}.")


