"""The /v1/restores resource — the mirror image of backups.

  POST /v1/restores       start a restore from a completed backup -> 202 + Job
  GET  /v1/restores/{id}  follow its progress                     -> 200 + Job
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ..jobs import store
from ..models import Job, JobStatus, StartRestoreRequest
from ..security import require_api_key
from ..services import pipeline

router = APIRouter(prefix="/v1/restores", tags=["restores"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
def start_restore(req: StartRestoreRequest, background: BackgroundTasks) -> Job:
    source = store.get(req.backup_id)
    if source is None or source.status != JobStatus.completed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,  # the request conflicts with current state
            detail="backup_id must refer to a completed backup.",
        )
    job = store.create("restore", source_drive=source.source_drive, target_drive=req.target_drive)
    background.add_task(pipeline.run_restore, job.id)
    return job


@router.get("/{job_id}", response_model=Job)
def get_restore(job_id: str) -> Job:
    job = store.get(job_id)
    if job is None or job.kind != "restore":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No restore with that id.")
    return job
