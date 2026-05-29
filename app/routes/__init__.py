"""API route modules."""

from app.routes.ask import router as ask_router
from app.routes.health import router as health_router
from app.routes.search import router as search_router
from app.routes.upload import router as upload_router

__all__ = ["ask_router", "health_router", "search_router", "upload_router"]
