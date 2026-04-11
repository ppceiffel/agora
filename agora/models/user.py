import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agora.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Pseudo optionnel — jamais le vrai nom (confidentialité)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Score citoyen éclairé
    enlightened_score: Mapped[int] = mapped_column(Integer, default=0)
    # Nombre de votes effectués
    votes_count: Mapped[int] = mapped_column(Integer, default=0)
    # Nombre de fois où l'utilisateur a lu des arguments opposés
    fairplay_count: Mapped[int] = mapped_column(Integer, default=0)

    # Profil Schwartz agrégé — recalculé après chaque vote
    # JSON : {"Liberté": 6.5, "Égalité": 7.2, "Fraternité": 8.0, ...}
    values_profile: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Marqueur pour l'utilisateur système agora-ai (seed arguments)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    votes = relationship("Vote", back_populates="user")
    arguments = relationship("Argument", back_populates="user")


class OTPCode(Base):
    __tablename__ = "otp_codes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number: Mapped[str] = mapped_column(String, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
