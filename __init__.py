"""3-2-1 Backup Automation Tool — internal API.

This package exposes the backup pipeline (image -> encrypt -> upload) over a
small local HTTP API. The system-tray UI and any other client talk to this API
instead of calling the pipeline functions directly.
"""

__version__ = "0.1.0"
