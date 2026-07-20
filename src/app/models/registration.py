import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.student import Student
from app.models.event import Event

class EventRegistration(Base):
    __tablename__ = 'event_registrations'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship("Student", back_populates="registrations")
    event: Mapped["Event"] = relationship("Event", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint('student_id', 'event_id', name='uq_student_event'),
    )
