from fastapi.routing import APIRouter

from wacruit.src.apps import announcement
from wacruit.src.apps import dummy
from wacruit.src.apps import portfolio
from wacruit.src.apps import problem

from wacruit.src.apps import user  # isort: skip
from wacruit.src.apps import resume  # isort: skip

api_router = APIRouter(prefix="/api")
api_router.include_router(announcement.router)
api_router.include_router(dummy.router)
api_router.include_router(portfolio.router)
api_router.include_router(problem.router)
api_router.include_router(user.router)
api_router.include_router(resume.router)
