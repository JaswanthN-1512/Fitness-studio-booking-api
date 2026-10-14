from datetime import datetime
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    class_id: int = Field(gt=0)


class BookingResponse(BaseModel):
    id: int
    class_id: int
    class_name: str
    user_id: int
    booked_at: datetime


class BookingListItem(BaseModel):
    booking_id: int
    class_id: int
    class_name: str
    instructor: str
    start_time: datetime
    booked_at: datetime
