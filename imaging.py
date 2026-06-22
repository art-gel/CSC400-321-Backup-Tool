"""Step 1 of the pipeline: image a drive.

REAL IMPLEMENTATION (your job): shell out to Windows' wbadmin / VSS to create a
full image of `source_drive`, and return the path to the resulting .vhd/.img.

For now this stub just simulates work so the API is fully runnable on any machine
(including Linux / CI) before the Windows-specific code exists.
"""

import time
from pathlib import Path


def create_image(source_drive: str, on_progress=None) -> Path:
    """Create a full image of `source_drive`. Returns the local image path.

    `on_progress` is an optional callback taking a float 0.0..1.0 so the caller
    (the pipeline) can update the job's progress while this runs.
    """
    # TODO(team): replace with:  wbadmin start backup -backupTarget:... -include:source_drive
    for pct in (0.25, 0.5, 0.75, 1.0):
        time.sleep(0.05)  # pretend imaging takes time
        if on_progress:
            on_progress(pct)
    return Path(f"/tmp/{source_drive.strip(':')}_image.img")
