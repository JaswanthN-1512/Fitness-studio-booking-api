import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import FitnessClass
from app.utils.timezone import IST

logger = logging.getLogger(__name__)


def create_class(db: Session, data) -> FitnessClass:
    fitness_class = FitnessClass(
        name=data.name.strip(), description=data.description.strip(), instructor=data.instructor.strip(),
        start_time=data.start_time, end_time=data.end_time, capacity=data.capacity, available_slots=data.capacity,
    )
    db.add(fitness_class)
    db.commit()
    db.refresh(fitness_class)
    logger.info("Class created successfully: class_id=%s", fitness_class.id)
    return fitness_class


def get_upcoming_classes(db: Session) -> list[FitnessClass]:
    now = datetime.now(IST)
    return list(db.scalars(select(FitnessClass).where(FitnessClass.start_time > now).order_by(FitnessClass.start_time.asc())).all())
