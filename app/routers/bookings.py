from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Booking, User
from app.schemas.booking import BookingCreate, BookingListItem, BookingResponse
from app.services.booking_service import BookingConflict, BookingService, ResourceNotFound

router = APIRouter(tags=["Bookings"])


@router.post("/book", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, summary="Book a fitness class")
def book(data: BookingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        booking = BookingService.create_booking(db, user, data.class_id)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BookingConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return BookingResponse(id=booking.id, class_id=booking.class_id, class_name=booking.fitness_class.name, user_id=booking.user_id, booked_at=booking.booked_at)


@router.get("/bookings", response_model=list[BookingListItem], summary="List the current user's bookings")
def bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Booking).where(Booking.user_id == user.id).order_by(Booking.booked_at.desc())).all()
    return [
        BookingListItem(
            booking_id=row.id,
            class_id=row.class_id,
            class_name=row.fitness_class.name,
            instructor=row.fitness_class.instructor,
            start_time=row.fitness_class.start_time,
            booked_at=row.booked_at,
        )
        for row in rows
    ]
