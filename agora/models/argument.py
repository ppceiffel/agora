import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agora.core.database import Base


class ArgumentPosition(str, Enum):
    POUR = "pour"
    CONTRE = "contre"


class Argument(Base):
    __tablename__ = "arguments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    referendum_id: Mapped[str] = mapped_column(String, ForeignKey("referendums.id"), nullable=False)
    position: Mapped[str] = mapped_column(String, nullable=False)  # ArgumentPosition
    content: Mapped[str] = mapped_column(Text, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="arguments")
    referendum = relationship("Referendum", back_populates="arguments")


class ArgumentRead(Base):
    """Trace les lectures d'arguments opposés pour le score Fair-Play."""
    __tablename__ = "argument_reads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    argument_id: Mapped[str] = mapped_column(String, ForeignKey("arguments.id"), nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
