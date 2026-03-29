from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agora.api.deps import get_current_user
from agora.core.database import get_db
from agora.models.referendum import QuizQuestion, Referendum
from agora.models.user import User

router = APIRouter(prefix="/referendums", tags=["referendums"])


class QuizQuestionOut(BaseModel):
    id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    order: int

    class Config:
        from_attributes = True


class ReferendumOut(BaseModel):
    id: str
    question: str
    summary: str
    source_url: str | None
    historical_context: str | None
    scientific_context: str | None
    week_start: datetime
    week_end: datetime

    class Config:
        from_attributes = True


class ReferendumDetailOut(ReferendumOut):
    quiz_questions: list[QuizQuestionOut]


@router.get("/current", response_model=ReferendumOut)
def get_current_referendum(db: Session = Depends(get_db)):
    """Retourne le référendum actif de la semaine."""
    now = datetime.utcnow()
    referendum = (
        db.query(Referendum)
        .filter(
            Referendum.is_active == True,
            Referendum.week_start <= now,
            Referendum.week_end >= now,
        )
        .first()
    )
    if not referendum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun référendum actif cette semaine.",
        )
    return referendum


@router.get("/{referendum_id}/quiz", response_model=list[QuizQuestionOut])
def get_quiz(
    referendum_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne les questions du quiz pour un référendum (authentification requise)."""
    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.referendum_id == referendum_id)
        .order_by(QuizQuestion.order)
        .all()
    )
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz introuvable pour ce référendum.",
        )
    return questions


class QuizAnswers(BaseModel):
    answers: dict[str, str]  # {question_id: "a" | "b" | "c"}


class QuizResult(BaseModel):
    passed: bool
    score: int
    total: int


@router.post("/{referendum_id}/quiz/validate", response_model=QuizResult)
def validate_quiz(
    referendum_id: str,
    payload: QuizAnswers,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Valide les réponses du quiz. Il faut 2/3 pour passer."""
    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.referendum_id == referendum_id)
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail="Quiz introuvable.")

    score = sum(
        1
        for q in questions
        if payload.answers.get(q.id) == q.correct_option
    )
    passed = score >= 2  # Seuil : 2 bonnes réponses sur 3

    return QuizResult(passed=passed, score=score, total=len(questions))
