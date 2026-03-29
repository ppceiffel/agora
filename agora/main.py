from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agora.api.auth.router import router as auth_router
from agora.api.referendum.router import router as referendum_router
from agora.api.votes.router import router as votes_router
from agora.core.config import settings
from agora.core.database import Base, engine

# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API du référendum intelligent — Agora",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(referendum_router)
app.include_router(votes_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
