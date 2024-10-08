from fastapi.routing import APIRouter

from wacruit.src.apps import announcement
from wacruit.src.apps import dummy
from wacruit.src.apps import portfolio
from wacruit.src.apps import problem
from wacruit.src.apps import recruiting
from wacruit.src.apps import resume
from wacruit.src.apps import user

api_router = APIRouter(prefix="/api")
api_router.include_router(dummy.router)
api_router.include_router(announcement.router)
api_router.include_router(user.router)
api_router.include_router(problem.v1_router)
api_router.include_router(problem.v2_router)
api_router.include_router(resume.router)
api_router.include_router(recruiting.router)
api_router.include_router(portfolio.v1_router)
api_router.include_router(portfolio.v2_router)
