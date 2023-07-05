from fastapi.routing import APIRouter

from wacruit.src.apps import dummy
from wacruit.src.apps import problem
from wacruit.src.apps import user

api_router = APIRouter()
api_router.include_router(dummy.router)
api_router.include_router(user.router)
api_router.include_router(problem.router)
