"""API-key authentication.

Even though this API only listens on localhost, you still don't want any random
process on the machine triggering restores or reading your S3 config. So every
protected endpoint requires the X-API-Key header to match the configured key.

`require_api_key` is a FastAPI dependency: any route that lists it as a parameter
will reject requests that don't carry a valid key, before the route code runs.
"""

from fastapi import Depends, Header, HTTPException, status

from .config import Settings, get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header.",
        )
