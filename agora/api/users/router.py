import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from agora.api.deps import get_current_user
from agora.core.database import get_db
from agora.models.referendum import Referendum
from agora.models.user import User
from agora.models.vote import Vote

router = APIRouter(prefix="/users", tags=["users"])

VALUES_LABELS = ["Liberté", "Égalité", "Fraternité", "Sécurité", "Justice", "Efficacité"]


# ── Schémas ────────────────────────────────────────────────────────────────────

class ValuesProfile(BaseModel):
    """Profil Schwartz agrégé sur tous les votes de l'utilisateur."""
    scores: dict[str, float]   # {"Liberté": 6.5, "Égalité": 7.2, ...}
    votes_count: int            # Nombre de votes pris en compte


class UserProfileOut(BaseModel):
    id: str
    nickname: str | None
    enlightened_score: int
    votes_count: int
    fairplay_count: int
    values_profile: ValuesProfile | None


class VoteHistoryItem(BaseModel):
    referendum_id: str
    question: str
    week_start: str
    grade: str
    values_scores: dict[str, float] | None  # Scores Schwartz pour CE vote


class PatchUserRequest(BaseModel):
    nickname: str

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Le pseudo doit faire au moins 2 caractères.")
        if len(v) > 50:
            raise ValueError("Le pseudo ne peut pas dépasser 50 caractères.")
        return v


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_values_profile(user: User) -> ValuesProfile | None:
    """Désérialise user.values_profile (JSON) en ValuesProfile."""
    if not user.values_profile:
        return None
    try:
        data = json.loads(user.values_profile)
        return ValuesProfile(scores=data.get("scores", {}), votes_count=data.get("votes_count", 0))
    except (json.JSONDecodeError, KeyError):
        return None


def _grade_to_values(grade: str, values_mapping: dict) -> dict[str, float] | None:
    """Mappe un grade JM vers les scores Schwartz grâce au mapping du référendum."""
    # Le grade en base est le slug snake_case, le mapping peut être en français ou en slug
    grade_map = {
        "tres_favorable": "Très favorable",
        "favorable": "Favorable",
        "neutre": "Neutre",
        "defavorable": "Défavorable",
        "tres_defavorable": "Très défavorable",
    }
    grade_label = grade_map.get(grade, grade)  # fallback si déjà en français
    scores_list = values_mapping.get(grade_label)
    if not scores_list or len(scores_list) != 6:
        return None
    return dict(zip(VALUES_LABELS, [float(s) for s in scores_list]))


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne le profil complet de l'utilisateur connecté."""
    return UserProfileOut(
        id=current_user.id,
        nickname=current_user.nickname,
        enlightened_score=current_user.enlightened_score,
        votes_count=current_user.votes_count,
        fairplay_count=current_user.fairplay_count,
        values_profile=_parse_values_profile(current_user),
    )


@router.patch("/me", response_model=UserProfileOut)
def update_my_profile(
    payload: PatchUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Met à jour le pseudo de l'utilisateur connecté."""
    # Vérifie que le pseudo n'est pas déjà pris
    existing = db.query(User).filter(
        User.nickname == payload.nickname,
        User.id != current_user.id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce pseudo est déjà utilisé.",
        )

    current_user.nickname = payload.nickname
    db.commit()
    db.refresh(current_user)
    return UserProfileOut(
        id=current_user.id,
        nickname=current_user.nickname,
        enlightened_score=current_user.enlightened_score,
        votes_count=current_user.votes_count,
        fairplay_count=current_user.fairplay_count,
        values_profile=_parse_values_profile(current_user),
    )


@router.get("/me/history", response_model=list[VoteHistoryItem])
def get_my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne l'historique des votes de l'utilisateur, du plus récent au plus ancien."""
    votes = (
        db.query(Vote)
        .filter(Vote.user_id == current_user.id)
        .order_by(Vote.created_at.desc())
        .all()
    )

    result = []
    for vote in votes:
        referendum = db.query(Referendum).filter(Referendum.id == vote.referendum_id).first()
        if not referendum:
            continue

        values_scores = None
        if referendum.values_mapping:
            try:
                mapping = json.loads(referendum.values_mapping)
                values_scores = _grade_to_values(vote.grade, mapping)
            except json.JSONDecodeError:
                pass

        result.append(VoteHistoryItem(
            referendum_id=referendum.id,
            question=referendum.question,
            week_start=referendum.week_start.strftime("%d/%m/%Y"),
            grade=vote.grade,
            values_scores=values_scores,
        ))

    return result
