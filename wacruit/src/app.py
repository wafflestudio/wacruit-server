from fastapi import FastAPI

from wacruit.src.admin import Admin
from wacruit.src.admin.auth import authentication_backend
from wacruit.src.admin.views import admin_views
from wacruit.src.apps.router import api_router
from wacruit.src.database.connection import DBSessionFactory
from wacruit.src.settings import settings


def _add_routers(app: FastAPI):
    app.include_router(router=api_router)


def _register_shutdown_event(app: FastAPI):
    @app.on_event("shutdown")
    def on_shutdown():
        DBSessionFactory().teardown()

    return on_shutdown


def _attach_admin(app: FastAPI):
    engine = DBSessionFactory().get_engine()
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        base_url="/api/admin",
        debug=not settings.is_prod,
    )
    for view in admin_views:
        admin.add_view(view)


def create_app() -> FastAPI:
    app = FastAPI(
        title="wacruit-server",
        debug=settings.is_dev,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    _add_routers(app)
    _attach_admin(app)
    _register_shutdown_event(app)
    return app
