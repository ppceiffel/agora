from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agora.api.deps import get_current_user
from agora.core.database import get_db
from agora.models.referendum import Referendum
from agora.models.user import User
from agora.models.vote import MajorityJudgmentGrade, Vote

router = APIRouter(prefix="/votes", tags=["votes"])

GRADE_ORDER = [
    MajorityJudgmentGrade.TRES_FAVORABLE,
    MajorityJudgmentGrade.FAVORABLE,
    MajorityJudgmentGrade.NEUTRE,
    MajorityJudgmentGrade.DEFAVORABLE,
    MajorityJudgmentGrade.TRES_DEFAVORABLE,
]

GRADE_LABELS = {
    MajorityJudgmentGrade.TRES_FAVORABLE: "Très favorable",
    MajorityJudgmentGrade.FAVORABLE: "Favorable",
    MajorityJudgmentGrade.NEUTRE: "Neutre",
    MajorityJudgmentGrade.DEFAVORABLE: "Défavorable",
    MajorityJudgmentGrade.TRES_DEFAVORABLE: "Très défavorable",
}


class CastVoteRequest(BaseModel):
    referendum_id: str
    grade: MajorityJudgmentGrade
    quiz_passed: bool


class VoteResultOut(BaseModel):
    referendum_id: str
    median_grade: str
    total_votes: int
    distribution: dict[str, int]


def compute_majority_judgment_median(grades: list[str]) -> str:
    """Calcule la médiane du Jugement Majoritaire."""
    if not grades:
        return MajorityJudgmentGrade.NEUTRE

    counts = Counter(grades)
    total = len(grades)
    cumulative = 0

    for grade in GRADE_ORDER:
        cumulative += counts.get(grade, 0)
        if cumulative >= total / 2:
            return grade

    return MajorityJudgmentGrade.NEUTRE


@router.post("/", status_code=status.HTTP_201_CREATED)
def cast_vote(
    payload: CastVoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enregistre le vote d'un citoyen (quiz requis)."""
    if not payload.quiz_passed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez réussir le quiz avant de voter.",
        )

    referendum = db.query(Referendum).filter(
        Referendum.id == payload.referendum_id,
        Referendum.is_active == True,
    ).first()
    if not referendum:
        raise HTTPException(status_code=404, detail="Référendum introuvable.")

    # Un seul vote par utilisateur par référendum
    existing = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.referendum_id == payload.referendum_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà voté pour ce référendum.",
        )

    vote = Vote(
        user_id=current_user.id,
        referendum_id=payload.referendum_id,
        grade=payload.grade,
        quiz_passed=payload.quiz_passed,
    )
    db.add(vote)

    current_user.votes_count += 1
    current_user.enlightened_score += 10

    db.commit()
    return {"message": "Vote enregistré."}


@router.get("/{referendum_id}/results", response_model=VoteResultOut)
def get_results(referendum_id: str, db: Session = Depends(get_db)):
    """Retourne les résultats en temps réel du Jugement Majoritaire."""
    votes = db.query(Vote).filter(Vote.referendum_id == referendum_id).all()

    grades = [v.grade for v in votes]
    distribution = {GRADE_LABELS[g]: grades.count(g) for g in GRADE_ORDER}
    median = compute_majority_judgment_median(grades)

    return VoteResultOut(
        referendum_id=referendum_id,
        median_grade=GRADE_LABELS[median],
        total_votes=len(grades),
        distribution=distribution,
    )
