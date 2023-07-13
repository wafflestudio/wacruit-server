import fastapi

from wacruit.src.apps.router import api_router
from wacruit.src.database.connection import DBSessionFactory
from wacruit.src.settings import settings


def _add_routers(app: fastapi.FastAPI):
    app.include_router(router=api_router)


def _register_shutdown_event(app: fastapi.FastAPI):
    @app.on_event("shutdown")
    def on_shutdown():
        DBSessionFactory().teardown()

    return on_shutdown


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI(title="wacruit-server", debug=settings.is_dev)
    _add_routers(app)
    _register_shutdown_event(app)
    return app
