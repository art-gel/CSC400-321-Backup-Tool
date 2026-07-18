
import uuid
import os
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
import pipeline
from scheduler import Scheduler
# from config import get_settings
from models import BackupRequest, RestoreRequest, Job, JobStatus
import os

app = FastAPI(title="3-2-1 Backup Tool")

script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notify_windows.py") # change notify_windows.py to WBAdmin_Script.py?
scheduler = Scheduler("321BackupTool", script_path=script_path)

TASK_NAME = "321BackupTool"
RUNNER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_scheduled_backup.py")
scheduler = Scheduler(TASK_NAME, script_path=RUNNER_SCRIPT)

@app.get("/health")
def health():
    # quick "is the server alive?" check
    return {"status": "ok", "scheduler_running": scheduler.is_running()}


@app.post("/backup", response_model=Job)
def start_backup(request: BackupRequest, background_tasks: BackgroundTasks):
    # 1. make a new job and put it on the scoreboard
    job = Job(
        id=str(uuid.uuid4()),
        kind="backup",
        status=JobStatus.queued,
        source_drive=request.source_drive,
    )
    pipeline.JOBS[job.id] = job
    # 2. run the slow work in the background so this request returns instantly.
    #    the passphrase is handed straight to the task. never stored on the job.
    background_tasks.add_task(pipeline.run_backup, job.id, request.passphrase)
    # 3. give the user their job (with its id) so they can check on it
    return job


@app.get("/backup/{job_id}", response_model=Job)
def get_backup(job_id: str):
    job = pipeline.JOBS.get(job_id)
    if job is None or job.kind != "backup":
        raise HTTPException(status_code=404, detail="no backup job with that id")
    return job


@app.post("/restore", response_model=Job)
def start_restore(request: RestoreRequest, background_tasks: BackgroundTasks):
    job = Job(
        id=str(uuid.uuid4()),
        kind="restore",
        status=JobStatus.queued,
        s3_key=request.s3_key,
    )
    pipeline.JOBS[job.id] = job
    background_tasks.add_task(pipeline.run_restore, job.id, request.passphrase)
    return job


@app.get("/restore/{job_id}", response_model=Job)
def get_restore(job_id: str):
    job = pipeline.JOBS.get(job_id)
    if job is None or job.kind != "restore":
        raise HTTPException(status_code=404, detail="no restore job with that id")
    return job



@app.get("/jobs", response_model=list[Job])
def scoreboard():
    return  list(pipeline.JOBS.values())


@app.delete("/backup/{job_id}") # this route returns one job
def delete_backup(job_id: str):
    job = pipeline.JOBS.get(job_id) # look up
    if job is None or job.kind != "backup": # is it real
        raise HTTPException(status_code=404, detail="no backup job with that id")
    if job.status == JobStatus.queued or job.status == JobStatus.uploading: # is it busy 
        raise HTTPException(status_code=409, detail="id is either running or queued")
    del pipeline.JOBS[job_id] # delete it
    return {"job_id":"deleted"} # confirm


@app.post("/schedule/start")
def schedule_start(minutes: Optional[int] = None):
    # turn on set-and-forget automatic backups.
    # leave minutes empty to use BACKUP_SCHEDULE_MINUTES from config.
    # safe to call twice: it overwrites the old task.
    every = minutes if minutes else get_settings().schedule_minutes
    if not scheduler.start(min=every):
        raise HTTPException(status_code=500, detail="could not create the task (needs Windows + admin)")
    return {"schedule": "started", "every_minutes": every}
 
 
@app.get("/schedule")
def schedule_status():
    # {'exists': bool, 'status': 'Ready' | 'Running' | 'Disabled' | 'Queued' | None}
    return scheduler.get_status()
 
 
@app.post("/schedule/stop")
def schedule_stop():
    # pause it. the task stays on the machine -- use /schedule/enable to resume.
    if not scheduler.exists():
        raise HTTPException(status_code=404, detail="no scheduled task")
    if not scheduler.disable():
        raise HTTPException(status_code=500, detail="could not stop the task")
    return {"schedule": "stopped"}
 
 
@app.post("/schedule/enable")
def schedule_enable():
    # un-pause it.
    if not scheduler.exists():
        raise HTTPException(status_code=404, detail="no scheduled task")
    if not scheduler.enable():
        raise HTTPException(status_code=500, detail="could not enable the task")
    return {"schedule": "enabled"}
 