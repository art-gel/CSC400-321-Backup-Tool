"""The data contracts.

These Pydantic models ARE the public face of the API. They define exactly what
a client must send and exactly what it gets back. FastAPI uses them to:
  - validate incoming JSON (reject bad requests automatically, 422)
  - serialize outgoing responses
  - generate the OpenAPI/Swagger docs

If your team agrees on these models first, the UI people and the pipeline people
can work in parallel against the same contract.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Every stage a backup (or restore) job can be in."""
    queued = "queued"
    imaging = "imaging"
    encrypting = "encrypting"
    uploading = "uploading"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# --------------------------------------------------------------------------- #
# Requests (what a client SENDS)
# --------------------------------------------------------------------------- #

class StartBackupRequest(BaseModel):
    source_drive: str = Field(examples=["C:"], description="Drive to image.")
    label: Optional[str] = Field(default=None, description="Optional human label.")


class StartRestoreRequest(BaseModel):
    backup_id: str = Field(description="ID of a completed backup to restore from.")
    target_drive: str = Field(examples=["D:"], description="Where to restore to.")


class ConfigUpdate(BaseModel):
    """All optional — clients send only the fields they want to change."""
    s3_bucket: Optional[str] = None
    aws_region: Optional[str] = None
    retention_count: Optional[int] = Field(default=None, ge=1, le=100)


# --------------------------------------------------------------------------- #
# Responses (what the API RETURNS)
# --------------------------------------------------------------------------- #

class Job(BaseModel):
    id: str
    kind: str                       # "backup" or "restore"
    status: JobStatus
    source_drive: Optional[str] = None
    target_drive: Optional[str] = None
    label: Optional[str] = None
    progress: float = 0.0           # 0.0 -> 1.0
    s3_key: Optional[str] = None    # set once uploaded
    error: Optional[str] = None     # set if status == failed
    created_at: datetime
    finished_at: Optional[datetime] = None


class ConfigView(BaseModel):
    s3_bucket: str
    aws_region: str
    retention_count: int


class HealthView(BaseModel):
    status: str = "ok"
    version: str
    active_jobs: int


class Message(BaseModel):
    """Generic envelope for simple acknowledgements and errors."""
    detail: str
