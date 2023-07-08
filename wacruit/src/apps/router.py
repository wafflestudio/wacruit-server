from importlib import import_module
from logging import getLogger

from fastapi.routing import APIRouter

from wacruit.src.settings import settings

logger = getLogger(__name__)

api_router = APIRouter()
for app in settings.apps:
    app_module = import_module(f"wacruit.src.apps.{app}")
    try:
        api_router.include_router(app_module.router)
    except AttributeError:
        logger.info("%s app doesn't have router", app)
