from fastapi.routing import APIRouter

from wacruit.src.apps.portfolio.file.views import v1_router as v1_file_router
from wacruit.src.apps.portfolio.url.views import v1_router as v1_url_router

v1_router = APIRouter(prefix="/v1/portfolios")
v1_router.include_router(v1_file_router)
v1_router.include_router(v1_url_router)

v2_router = APIRouter(prefix="/v2/portfolios")
