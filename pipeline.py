"""The orchestrator: glues image -> encrypt -> upload into one job.

This is what runs in the background after POST /v1/backups returns. It walks the
job through each stage, updating the JobStore so a polling client sees progress.
The routers never call imaging/encryption/storage directly — they call this.
"""

from datetime import datetime, timezone

from ..config import get_settings
from ..jobs import store
from ..models import JobStatus
from . import encryption, imaging, storage


def _now():
    return datetime.now(timezone.utc)


def run_backup(job_id: str) -> None:
    settings = get_settings()
    try:
        job = store.get(job_id)
        if job is None:
            return

        # Stage 1: image
        store.update(job_id, status=JobStatus.imaging, progress=0.0)
        image_path = imaging.create_image(
            job.source_drive,
            on_progress=lambda p: store.update(job_id, progress=round(p * 0.5, 3)),
        )

        # Stage 2: encrypt
        store.update(job_id, status=JobStatus.encrypting)
        enc_path = encryption.encrypt_file(
            image_path,
            on_progress=lambda p: store.update(job_id, progress=round(0.5 + p * 0.2, 3)),
        )

        # Stage 3: upload
        store.update(job_id, status=JobStatus.uploading)
        key = storage.upload(
            enc_path,
            bucket=settings.s3_bucket,
            region=settings.aws_region,
            on_progress=lambda p: store.update(job_id, progress=round(0.7 + p * 0.3, 3)),
        )

        store.update(
            job_id,
            status=JobStatus.completed,
            progress=1.0,
            s3_key=key,
            finished_at=_now(),
        )
    except Exception as exc:  # any stage failing marks the whole job failed
        store.update(job_id, status=JobStatus.failed, error=str(exc), finished_at=_now())


def run_restore(job_id: str) -> None:
    """Placeholder mirror of run_backup: download -> decrypt -> write image."""
    try:
        store.update(job_id, status=JobStatus.uploading, progress=0.5)  # reuse stages loosely
        # TODO(team): storage.download -> encryption.decrypt -> imaging.apply
        store.update(job_id, status=JobStatus.completed, progress=1.0, finished_at=_now())
    except Exception as exc:
        store.update(job_id, status=JobStatus.failed, error=str(exc), finished_at=_now())
