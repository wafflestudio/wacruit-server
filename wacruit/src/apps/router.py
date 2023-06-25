from fastapi.routing import APIRouter

# from wacruit.src.apps import user
from wacruit.src.apps import announcement
from wacruit.src.apps import dummy

api_router = APIRouter()
api_router.include_router(dummy.router)
api_router.include_router(announcement.router)
# api_router.include_router(user.router)
