from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.fitness_class import FitnessClassCreate, FitnessClassResponse
from app.services.class_service import create_class, get_upcoming_classes

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=list[FitnessClassResponse], summary="List upcoming fitness classes")
def list_classes(db: Session = Depends(get_db)):
    return get_upcoming_classes(db)


@router.post("", response_model=FitnessClassResponse, status_code=status.HTTP_201_CREATED, summary="Create a fitness class")
def add_class(data: FitnessClassCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_class(db, data)
