"""Health check — the one endpoint with no auth.

The tray UI hits this on startup to confirm the backup service is alive before
showing its menu. Monitoring tools use this kind of endpoint too.
"""

from fastapi import APIRouter

from .. import __version__
from ..jobs import store
from ..models import HealthView

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthView)
def health() -> HealthView:
    return HealthView(version=__version__, active_jobs=store.active_count())
