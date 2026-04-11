"""
Router admin — endpoints protégés par X-Admin-Secret.
Permet de déclencher le pipeline AI manuellement et de consulter tous les référendums.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agora.core.config import settings
from agora.core.database import get_db
from agora.models.referendum import Referendum

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Dépendance d'authentification admin ───────────────────────────────────────

def require_admin(x_admin_secret: str = Header(...)):
    """Vérifie le header X-Admin-Secret."""
    if not settings.admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé.",
        )


# ── Schémas ────────────────────────────────────────────────────────────────────

class ReferendumAdminOut(BaseModel):
    id: str
    question: str
    is_active: bool
    week_start: datetime
    week_end: datetime
    created_at: datetime
    news_source_title: str | None
    votes_count: int

    class Config:
        from_attributes = True


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/referendums", response_model=list[ReferendumAdminOut])
def list_referendums(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Liste tous les référendums (actifs et archivés), du plus récent au plus ancien."""
    referendums = (
        db.query(Referendum)
        .order_by(Referendum.created_at.desc())
        .all()
    )
    result = []
    for ref in referendums:
        result.append(ReferendumAdminOut(
            id=ref.id,
            question=ref.question,
            is_active=ref.is_active,
            week_start=ref.week_start,
            week_end=ref.week_end,
            created_at=ref.created_at,
            news_source_title=ref.news_source_title,
            votes_count=len(ref.votes),
        ))
    return result


@router.post("/generate-referendum", status_code=status.HTTP_202_ACCEPTED)
def trigger_generate_referendum(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """
    Déclenche le pipeline AI de génération de référendum manuellement.
    Retourne 202 Accepted immédiatement — la génération tourne en arrière-plan.
    En Phase 2, cet endpoint appellera scheduler.run_pipeline_now().
    """
    # Phase 1 : stub — le pipeline AI sera branché en Phase 2
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY non configurée. Ajoutez-la dans .env pour utiliser le pipeline AI.",
        )

    # Vérification : ne pas générer si un référendum actif existe déjà cette semaine
    now = datetime.utcnow()
    active = db.query(Referendum).filter(
        Referendum.is_active == True,
        Referendum.week_start <= now,
        Referendum.week_end >= now,
    ).first()
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un référendum actif existe déjà cette semaine (id: {active.id}). "
                   "Désactivez-le d'abord ou attendez la semaine prochaine.",
        )

    # En Phase 2, on appellera ici : await pipeline.run()
    return {
        "message": "Pipeline AI branché en Phase 2. Configurez ANTHROPIC_API_KEY et relancez.",
        "status": "pending_phase2",
    }


@router.patch("/referendums/{referendum_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_referendum(
    referendum_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Désactive un référendum (utile avant d'en créer un nouveau manuellement)."""
    ref = db.query(Referendum).filter(Referendum.id == referendum_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Référendum introuvable.")
    ref.is_active = False
    db.commit()
    return {"message": f"Référendum {referendum_id} désactivé."}
