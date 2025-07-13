from fastapi.routing import APIRouter

from wacruit.src.apps import announcement
from wacruit.src.apps import dummy
from wacruit.src.apps import history
from wacruit.src.apps import member
from wacruit.src.apps import portfolio
from wacruit.src.apps import problem
from wacruit.src.apps import project
from wacruit.src.apps import recruiting
from wacruit.src.apps import resume
from wacruit.src.apps import review
from wacruit.src.apps import seminar
from wacruit.src.apps import user

api_router = APIRouter(prefix="/api")
api_router.include_router(dummy.router)
api_router.include_router(announcement.router)
api_router.include_router(user.router)
api_router.include_router(member.router)
api_router.include_router(problem.v1_router)
api_router.include_router(problem.v2_router)
api_router.include_router(resume.router)
api_router.include_router(recruiting.v1_router)
api_router.include_router(recruiting.v3_router)
api_router.include_router(portfolio.v1_router)
api_router.include_router(portfolio.v2_router)
api_router.include_router(project.router)
api_router.include_router(seminar.router)
api_router.include_router(history.router)
api_router.include_router(review.router)
