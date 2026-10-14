import logging
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Booking, FitnessClass, User
from app.utils.timezone import IST

logger = logging.getLogger(__name__)


class BookingConflict(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class BookingService:
    @staticmethod
    def create_booking(db: Session, user: User, class_id: int) -> Booking:
        fitness_class = db.scalar(select(FitnessClass).where(FitnessClass.id == class_id))
        if not fitness_class:
            raise ResourceNotFound("Class not found")
        now = datetime.now(IST)
        if fitness_class.start_time <= now:
            raise BookingConflict("Class has already started")

        existing = db.scalar(select(Booking).where(Booking.user_id == user.id, Booking.class_id == class_id))
        if existing:
            raise BookingConflict("User has already booked this class")

        # SQLite-safe atomic conditional decrement. Only one transaction can
        # successfully reduce a slot when available_slots > 0.
        result = db.execute(
            update(FitnessClass)
            .where(FitnessClass.id == class_id, FitnessClass.available_slots > 0)
            .values(available_slots=FitnessClass.available_slots - 1)
        )
        if result.rowcount != 1:
            raise BookingConflict("Class is fully booked")

        booking = Booking(user_id=user.id, class_id=class_id)
        db.add(booking)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            logger.warning("Duplicate booking prevented: user_id=%s class_id=%s", user.id, class_id)
            raise BookingConflict("User has already booked this class")
        db.refresh(booking)
        logger.info("Booking created successfully: booking_id=%s", booking.id)
        return booking
