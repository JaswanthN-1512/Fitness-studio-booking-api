from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, ISTDateTime


class FitnessClass(Base):
    __tablename__ = "fitness_classes"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_class_capacity_positive"),
        CheckConstraint("available_slots >= 0", name="ck_class_available_nonnegative"),
        CheckConstraint("available_slots <= capacity", name="ck_class_available_lte_capacity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    instructor: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[datetime] = mapped_column(ISTDateTime(), nullable=False)
    end_time: Mapped[datetime] = mapped_column(ISTDateTime(), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    available_slots: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(ISTDateTime(), default=lambda: datetime.now(timezone.utc), nullable=False)

    bookings = relationship("Booking", back_populates="fitness_class", cascade="all, delete-orphan")
