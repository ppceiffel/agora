import json
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agora.api.deps import get_current_user
from agora.core.database import get_db
from agora.models.argument import Argument, ArgumentRead
from agora.models.referendum import Referendum
from agora.models.user import User
from agora.models.vote import MajorityJudgmentGrade, Vote

router = APIRouter(prefix="/votes", tags=["votes"])

VALUES_LABELS = ["Liberté", "Égalité", "Fraternité", "Sécurité", "Justice", "Efficacité"]

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

# Mapping slug → label français (pour retrouver le grade dans values_mapping)
GRADE_SLUG_TO_LABEL = {g.value: label for g, label in GRADE_LABELS.items()}


# ── Schémas ────────────────────────────────────────────────────────────────────

class CastVoteRequest(BaseModel):
    referendum_id: str
    grade: MajorityJudgmentGrade
    quiz_passed: bool


class VoteResultOut(BaseModel):
    referendum_id: str
    median_grade: str
    total_votes: int
    distribution: dict[str, int]
    distribution_pct: dict[str, float]


# ── Calcul Jugement Majoritaire ────────────────────────────────────────────────

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


# ── Middleware Schwartz ─────────────────────────────────────────────────────────

def _update_values_profile(user: User, new_vote: Vote, referendum: Referendum, db: Session) -> None:
    """
    Recalcule et sauvegarde user.values_profile après un nouveau vote.
    Moyenne des scores Schwartz sur tous les votes de l'utilisateur.
    """
    if not referendum.values_mapping:
        return

    try:
        mapping = json.loads(referendum.values_mapping)
    except json.JSONDecodeError:
        return

    # Récupère tous les votes de l'utilisateur (y compris le nouveau, déjà en session)
    all_votes = db.query(Vote).filter(Vote.user_id == user.id).all()

    all_score_vectors: list[list[float]] = []
    for vote in all_votes:
        ref = db.query(Referendum).filter(Referendum.id == vote.referendum_id).first()
        if not ref or not ref.values_mapping:
            continue
        try:
            ref_mapping = json.loads(ref.values_mapping)
        except json.JSONDecodeError:
            continue

        grade_label = GRADE_SLUG_TO_LABEL.get(vote.grade, vote.grade)
        scores_list = ref_mapping.get(grade_label)
        if scores_list and len(scores_list) == 6:
            all_score_vectors.append([float(s) for s in scores_list])

    if not all_score_vectors:
        return

    n = len(all_score_vectors)
    avg_scores = [
        sum(vec[i] for vec in all_score_vectors) / n
        for i in range(6)
    ]

    user.values_profile = json.dumps({
        "scores": dict(zip(VALUES_LABELS, [round(s, 2) for s in avg_scores])),
        "votes_count": n,
    })


# ── Endpoints ──────────────────────────────────────────────────────────────────

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
    db.flush()  # génère l'id du vote sans committer

    # ── Mise à jour du score citoyen ──────────────────────────────────────────
    current_user.votes_count += 1
    current_user.enlightened_score += 10  # bonus vote

    if payload.quiz_passed:
        current_user.enlightened_score += 10  # bonus quiz

    # Bonus Fair-Play : a-t-il lu des arguments de ce référendum ?
    reads = (
        db.query(ArgumentRead)
        .join(Argument, Argument.id == ArgumentRead.argument_id)
        .filter(
            ArgumentRead.user_id == current_user.id,
            Argument.referendum_id == payload.referendum_id,
        )
        .count()
    )
    if reads >= 2:  # au moins 2 arguments lus (idéalement des deux camps)
        current_user.enlightened_score += 5  # bonus fair-play
        current_user.fairplay_count += 1

    # ── Mise à jour du profil de valeurs Schwartz ─────────────────────────────
    _update_values_profile(current_user, vote, referendum, db)

    db.commit()
    return {
        "message": "Vote enregistré.",
        "enlightened_score": current_user.enlightened_score,
    }


@router.get("/{referendum_id}/results", response_model=VoteResultOut)
def get_results(referendum_id: str, db: Session = Depends(get_db)):
    """Retourne les résultats en temps réel du Jugement Majoritaire."""
    votes = db.query(Vote).filter(Vote.referendum_id == referendum_id).all()

    grades = [v.grade for v in votes]
    total = len(grades)
    distribution = {GRADE_LABELS[g]: grades.count(g) for g in GRADE_ORDER}
    distribution_pct = {
        label: round(count / total * 100, 1) if total > 0 else 0.0
        for label, count in distribution.items()
    }
    median = compute_majority_judgment_median(grades)

    return VoteResultOut(
        referendum_id=referendum_id,
        median_grade=GRADE_LABELS[median],
        total_votes=total,
        distribution=distribution,
        distribution_pct=distribution_pct,
    )
