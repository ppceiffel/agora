import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agora.core.database import Base


class MajorityJudgmentGrade(str, Enum):
    TRES_FAVORABLE = "tres_favorable"
    FAVORABLE = "favorable"
    NEUTRE = "neutre"
    DEFAVORABLE = "defavorable"
    TRES_DEFAVORABLE = "tres_defavorable"


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    referendum_id: Mapped[str] = mapped_column(String, ForeignKey("referendums.id"), nullable=False)
    grade: Mapped[str] = mapped_column(String, nullable=False)  # MajorityJudgmentGrade
    quiz_passed: Mapped[bool] = mapped_column(String, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="votes")
    referendum = relationship("Referendum", back_populates="votes")
