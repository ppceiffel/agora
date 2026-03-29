import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agora.core.database import Base


class Referendum(Base):
    __tablename__ = "referendums"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)  # Résumé du sujet
    source_url: Mapped[str] = mapped_column(String, nullable=True)  # Source scrappée
    historical_context: Mapped[str] = mapped_column(Text, nullable=True)  # Éclairage historique
    scientific_context: Mapped[str] = mapped_column(Text, nullable=True)  # Éclairage scientifique
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    week_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    week_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quiz_questions = relationship("QuizQuestion", back_populates="referendum")
    votes = relationship("Vote", back_populates="referendum")
    arguments = relationship("Argument", back_populates="referendum")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    referendum_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String, nullable=False)
    option_b: Mapped[str] = mapped_column(String, nullable=False)
    option_c: Mapped[str] = mapped_column(String, nullable=False)
    correct_option: Mapped[str] = mapped_column(String, nullable=False)  # "a", "b" ou "c"
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    referendum = relationship("Referendum", back_populates="quiz_questions")
