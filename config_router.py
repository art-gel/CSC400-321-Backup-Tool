"""The /v1/config resource — read and update the tool's settings.

  GET /v1/config   what bucket/region/retention are we using? -> 200 + ConfigView
  PUT /v1/config   change one or more of them                 -> 200 + ConfigView

PUT (not POST) because the client is replacing/updating an existing settings
object, and PUT is idempotent: sending the same update twice leaves the same
result. The settings panel in the tray UI is backed by these two endpoints.
"""

from fastapi import APIRouter, Depends

from ..config import Settings, get_settings
from ..models import ConfigUpdate, ConfigView
from ..security import require_api_key

router = APIRouter(prefix="/v1/config", tags=["config"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=ConfigView)
def read_config(settings: Settings = Depends(get_settings)) -> ConfigView:
    return ConfigView(
        s3_bucket=settings.s3_bucket,
        aws_region=settings.aws_region,
        retention_count=settings.retention_count,
    )


@router.put("", response_model=ConfigView)
def update_config(update: ConfigUpdate, settings: Settings = Depends(get_settings)) -> ConfigView:
    # NOTE: this mutates the in-memory Settings for the demo. In the real tool,
    # persist these to a config file (e.g. %APPDATA%/backup-tool/config.json) so
    # they survive restarts.
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(settings, field, value)
    return ConfigView(
        s3_bucket=settings.s3_bucket,
        aws_region=settings.aws_region,
        retention_count=settings.retention_count,
    )
