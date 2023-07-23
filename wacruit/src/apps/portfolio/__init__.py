from fastapi.routing import APIRouter

from wacruit.src.apps.portfolio.file.views import v1_router as file_router
from wacruit.src.apps.portfolio.url.views import v1_router as url_router

router = APIRouter(prefix="/v1/portfolios", tags=["portfolios"])
router.include_router(file_router)
router.include_router(url_router)
