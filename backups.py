"""The /v1/backups resource.

This is the textbook example of mapping a real-world thing (a backup) onto REST:

  POST   /v1/backups        create a backup  -> 202 Accepted + the new Job
  GET    /v1/backups        list all backups -> 200 + [Job]
  GET    /v1/backups/{id}   read one         -> 200 + Job   (404 if unknown)
  DELETE /v1/backups/{id}   cancel/remove    -> 200 + message (404 if unknown)

Notice POST returns 202 (Accepted), not 200/201: the backup hasn't *happened*
yet, we've only accepted it and started it in the background. The client polls
GET /v1/backups/{id} to follow it to completion.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from ..jobs import store
from ..models import Job, JobStatus, Message, StartBackupRequest
from ..security import require_api_key
from ..services import pipeline

router = APIRouter(prefix="/v1/backups", tags=["backups"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=Job, status_code=status.HTTP_202_ACCEPTED)
def start_backup(req: StartBackupRequest, background: BackgroundTasks) -> Job:
    job = store.create("backup", source_drive=req.source_drive, label=req.label)
    # Hand the slow work to the background; the response returns immediately.
    background.add_task(pipeline.run_backup, job.id)
    return job


@router.get("", response_model=list[Job])
def list_backups() -> list[Job]:
    return [j for j in store.list() if j.kind == "backup"]


@router.get("/{job_id}", response_model=Job)
def get_backup(job_id: str) -> Job:
    job = store.get(job_id)
    if job is None or job.kind != "backup":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No backup with that id.")
    return job


@router.delete("/{job_id}", response_model=Message)
def cancel_backup(job_id: str) -> Message:
    job = store.get(job_id)
    if job is None or job.kind != "backup":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No backup with that id.")
    # If still running, mark cancelled; either way drop it from the store.
    if job.status not in {JobStatus.completed, JobStatus.failed}:
        store.update(job_id, status=JobStatus.cancelled)
    store.delete(job_id)
    return Message(detail=f"Backup {job_id} removed.")
