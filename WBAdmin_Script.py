from __future__ import annotations
import os , re , subprocess, sys, time
from pathlib import Path
# os reads envirnment setting
# re does text pattern matching
# subprocess allows outside program(wbadmin) to run and listens to it
# sys tells algorithm which os its currently on
# path handles file locations
 
DEFAULT_TARGET = os.environ.get("BACKUP_TARGET", "E:")
IMAGE_FOLDER_NAME = "WindowsImageBackup"
PERCENTAGE = re.compile(r"(\d{1,3})%")

# am i runnning on windows? (receptionist)
def create_image(source_drive: str, on_progress=None, target_drive: str = DEFAULT_TARGET) -> Path:
   
    if sys.platform.startswith("windows"):
        return _create_image_wbadmin(source_drive, on_progress, target_drive)
    

def _create_image_wbadmin(source_drive, on_progress, target_drive) -> Path:
   
   # add more wdamdin controls. create regular backups function

   
    cmd = [
        "wbadmin start backup",
        f"backup target:{target_drive}",
        f"-includes the following:{source_drive}",
        "-allCritical",   # specify all critical volumes that are to be included in backup
        "-vssFull",       # perform a full backup using the volume shadow copy service
        "-quiet",         # runs the command automatically/without prompts
    ]
    print("Back up in Process, come back later:", " ".join(cmd))

    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, # gets programs output/ python can read it
        stderr=subprocess.STDOUT,   #directs errors to same pipeline as reg messages 
        text=True,                  # string format
        bufsize=1,                  # spacing
    )

    last_pct = -1
    assert process.stdout is not None   

    for line in process.stdout:
        print(line, end="")             
        match = PERCENTAGE.search(line)
        if match and on_progress:
            pct = min(int(match.group(1)), 100)
            if pct != last_pct:         
                last_pct = pct
                on_progress(pct / 100.0)

    returncode = process.wait()

    if returncode == 0 and on_progress(1.0):          
        print("Backup completed successfully!")
    else:
        print(f"Backup failed with exit code {returncode}.")

    return Path(target_drive) / IMAGE_FOLDER_NAME # fix this 

# add redundancy here#######################


#self-testing only
if __name__ == "__main__":  
    img = create_image("C:", on_progress=lambda p: print(f"  progress: {p:.0%}"))
    print("Image at:", img)
