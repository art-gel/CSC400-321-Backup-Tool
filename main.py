"""Application entry point.

`create_app()` builds the FastAPI instance and mounts every router. Keeping this
in a factory (rather than a module-level `app = FastAPI()`) makes it easy for the
test suite to spin up a fresh app, and keeps wiring in one readable place.

Run it locally with:
    uvicorn backup_api.main:app --reload --port 8787

Then open http://127.0.0.1:8787/docs for the auto-generated, interactive API docs.
"""



from fastapi import FastAPI

from . import __version__
from .routers import backups, config_router, health, restores


def create_app() -> FastAPI:
    app = FastAPI(
        title="3-2-1 Backup Tool API",
        version=__version__,
        description=(
            #more work needs to be done
            
        ),
    )

    # Order doesn't matter; each router carries its own prefix.
    app.include_router(health.router)
    app.include_router(backups.router)
    app.include_router(restores.router)
    app.include_router(config_router.router)

    return app


app = create_app()
