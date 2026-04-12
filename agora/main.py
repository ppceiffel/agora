import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agora.api.admin.router import router as admin_router
from agora.api.arguments.router import router as arguments_router
from agora.api.auth.router import router as auth_router
from agora.api.referendum.router import router as referendum_router
from agora.api.users.router import router as users_router
from agora.api.votes.router import router as votes_router
from agora.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    description="API du référendum intelligent — Agora",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(referendum_router)
app.include_router(votes_router)
app.include_router(arguments_router)
app.include_router(users_router)
app.include_router(admin_router)


@app.on_event("startup")
def startup_event() -> None:
    """Démarre le scheduler hebdomadaire au lancement de l'API."""
    from agora.core.scheduler import start_scheduler
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Arrête proprement le scheduler à l'extinction de l'API."""
    from agora.core.scheduler import stop_scheduler
    stop_scheduler()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.app_name}
