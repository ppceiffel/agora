from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from agora.api.deps import get_current_user
from agora.core.database import get_db
from agora.models.argument import Argument, ArgumentRead, ArgumentVote
from agora.models.referendum import Referendum
from agora.models.user import User

router = APIRouter(prefix="/arguments", tags=["arguments"])

TOP_N = 3  # Nombre d'arguments par camp retournés dans le GET


# ── Schémas ────────────────────────────────────────────────────────────────────

class ArgumentOut(BaseModel):
    id: str
    position: str         # "pour" | "contre"
    content: str
    upvotes: int
    is_seed: bool         # True si auteur = agora-ai (is_system)
    author_nickname: str | None

    class Config:
        from_attributes = True


class ArgumentsOut(BaseModel):
    pour: list[ArgumentOut]
    contre: list[ArgumentOut]


class SubmitArgumentRequest(BaseModel):
    referendum_id: str
    position: str
    content: str

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: str) -> str:
        if v not in ("pour", "contre"):
            raise ValueError("position doit être 'pour' ou 'contre'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 20:
            raise ValueError("L'argument doit faire au moins 20 caractères.")
        if len(v) > 500:
            raise ValueError("L'argument ne peut pas dépasser 500 caractères.")
        return v


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_out(arg: Argument, db: Session) -> ArgumentOut:
    return ArgumentOut(
        id=arg.id,
        position=arg.position,
        content=arg.content,
        upvotes=arg.upvotes,
        is_seed=arg.user.is_system if arg.user else False,
        author_nickname=arg.user.nickname if arg.user and not arg.user.is_system else None,
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/{referendum_id}", response_model=ArgumentsOut)
def get_arguments(referendum_id: str, db: Session = Depends(get_db)):
    """Retourne les top 3 arguments pour et contre, triés par upvotes."""
    referendum = db.query(Referendum).filter(Referendum.id == referendum_id).first()
    if not referendum:
        raise HTTPException(status_code=404, detail="Référendum introuvable.")

    def top(position: str) -> list[ArgumentOut]:
        args = (
            db.query(Argument)
            .filter(
                Argument.referendum_id == referendum_id,
                Argument.position == position,
                Argument.is_moderated == True,
            )
            .order_by(Argument.upvotes.desc())
            .limit(TOP_N)
            .all()
        )
        return [_to_out(a, db) for a in args]

    return ArgumentsOut(pour=top("pour"), contre=top("contre"))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ArgumentOut)
def submit_argument(
    payload: SubmitArgumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soumet un argument citoyen (nécessite d'avoir voté sur ce référendum)."""
    referendum = db.query(Referendum).filter(
        Referendum.id == payload.referendum_id,
        Referendum.is_active == True,
    ).first()
    if not referendum:
        raise HTTPException(status_code=404, detail="Référendum introuvable ou clôturé.")

    # Limite : 1 argument par position par utilisateur par référendum
    existing = db.query(Argument).filter(
        Argument.user_id == current_user.id,
        Argument.referendum_id == payload.referendum_id,
        Argument.position == payload.position,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vous avez déjà soumis un argument '{payload.position}' pour ce référendum.",
        )

    arg = Argument(
        user_id=current_user.id,
        referendum_id=payload.referendum_id,
        position=payload.position,
        content=payload.content,
        upvotes=0,
        is_moderated=False,  # en attente de modération
    )
    db.add(arg)
    db.commit()
    db.refresh(arg)
    return _to_out(arg, db)


@router.post("/{argument_id}/upvote", status_code=status.HTTP_201_CREATED)
def upvote_argument(
    argument_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upvote un argument (1 upvote par utilisateur par argument)."""
    arg = db.query(Argument).filter(Argument.id == argument_id).first()
    if not arg:
        raise HTTPException(status_code=404, detail="Argument introuvable.")

    already = db.query(ArgumentVote).filter(
        ArgumentVote.user_id == current_user.id,
        ArgumentVote.argument_id == argument_id,
    ).first()
    if already:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà upvoté cet argument.",
        )

    db.add(ArgumentVote(user_id=current_user.id, argument_id=argument_id))
    arg.upvotes += 1
    db.commit()
    return {"message": "Upvote enregistré.", "upvotes": arg.upvotes}


@router.delete("/{argument_id}/upvote", status_code=status.HTTP_200_OK)
def remove_upvote(
    argument_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retire l'upvote d'un argument."""
    arg = db.query(Argument).filter(Argument.id == argument_id).first()
    if not arg:
        raise HTTPException(status_code=404, detail="Argument introuvable.")

    vote = db.query(ArgumentVote).filter(
        ArgumentVote.user_id == current_user.id,
        ArgumentVote.argument_id == argument_id,
    ).first()
    if not vote:
        raise HTTPException(status_code=404, detail="Vous n'avez pas upvoté cet argument.")

    db.delete(vote)
    arg.upvotes = max(0, arg.upvotes - 1)
    db.commit()
    return {"message": "Upvote retiré.", "upvotes": arg.upvotes}


@router.post("/{argument_id}/read", status_code=status.HTTP_200_OK)
def mark_argument_read(
    argument_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trace la lecture d'un argument (alimente le score Fair-Play)."""
    arg = db.query(Argument).filter(Argument.id == argument_id).first()
    if not arg:
        raise HTTPException(status_code=404, detail="Argument introuvable.")

    # Idempotent : une seule trace par argument par utilisateur
    already_read = db.query(ArgumentRead).filter(
        ArgumentRead.user_id == current_user.id,
        ArgumentRead.argument_id == argument_id,
    ).first()
    if already_read:
        return {"message": "Déjà marqué comme lu.", "fairplay_bonus": 0}

    db.add(ArgumentRead(user_id=current_user.id, argument_id=argument_id))

    # Bonus Fair-Play : +1 par lecture d'un argument du camp opposé (plafonné à 5)
    current_user.fairplay_count += 1
    if current_user.fairplay_count <= 5:
        current_user.enlightened_score += 1

    db.commit()
    return {"message": "Lecture enregistrée.", "fairplay_bonus": 1}
