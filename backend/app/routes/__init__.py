from .web_routes import router as web_router
from .user_routes import router as user_router
from .workout_routes import router as workout_router
from .feedback_routes import router as feedback_router
from .admin_routes import router as admin_router

__all__ = ["web_router", "user_router", "workout_router", "feedback_router", "admin_router"]
