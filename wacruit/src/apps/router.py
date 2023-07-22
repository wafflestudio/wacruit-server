from fastapi.routing import APIRouter

from wacruit.src.apps.announcement.views import v1_router as announcement_router
from wacruit.src.apps.dummy.views import v1_router as dummy_router
from wacruit.src.apps.problem.views import v1_router as problem_router
from wacruit.src.apps.recruiting.views import v1_router as recruiting_router
from wacruit.src.apps.resume.views import v1_router as resume_router
from wacruit.src.apps.user.views import v1_router as user_router

api_router = APIRouter(prefix="/api")
api_router.include_router(dummy_router)
api_router.include_router(announcement_router)
api_router.include_router(user_router)
api_router.include_router(problem_router)
api_router.include_router(resume_router)
api_router.include_router(recruiting_router)
