"""Database models using SQLAlchemy."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Lead(Base):
    """Lead model representing a WhatsApp lead from Monday.com."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monday_item_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String)
    lead_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="לייד חדש")
    
    # Initial message scheduling (6-minute delay)
    first_message_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_message_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Follow-up scheduling (24h after first message)
    followup_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_leads_followup_due_is_done", "followup_due_at", "is_done"),
        Index("ix_leads_first_message_due", "first_message_due_at", "first_message_sent"),
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, monday_item_id={self.monday_item_id}, status={self.status})>"
