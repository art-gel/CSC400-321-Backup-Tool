"""A tiny in-memory store of jobs.

Backups take minutes (imaging a whole drive is slow), so the API cannot finish
the work inside a single HTTP request. Instead it creates a Job, kicks the work
off in the background, and hands the client a job ID. The client then polls
GET /v1/backups/{id} to watch the status move queued -> imaging -> ... -> completed.

For the capstone, an in-memory dict is fine. If you later want jobs to survive a
restart of the service, swap this class for one backed by SQLite — the rest of
the app won't need to change because everything goes through this interface.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import Job, JobStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()  # background tasks + requests touch this concurrently

    def create(self, kind: str, **fields) -> Job:
        job = Job(
            id=uuid.uuid4().hex[:12],
            kind=kind,
            status=JobStatus.queued,
            created_at=_now(),
            **fields,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> List[Job]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    def update(self, job_id: str, **fields) -> Optional[Job]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            updated = job.model_copy(update=fields)
            self._jobs[job_id] = updated
            return updated

    def delete(self, job_id: str) -> bool:
        with self._lock:
            return self._jobs.pop(job_id, None) is not None

    def active_count(self) -> int:
        terminal = {JobStatus.completed, JobStatus.failed, JobStatus.cancelled}
        with self._lock:
            return sum(1 for j in self._jobs.values() if j.status not in terminal)


# One shared store for the whole process.
store = JobStore()
