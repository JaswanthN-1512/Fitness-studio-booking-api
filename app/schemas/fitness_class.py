from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.utils.timezone import IST


class FitnessClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    instructor: str = Field(min_length=1, max_length=100)
    start_time: datetime
    end_time: datetime
    capacity: int = Field(gt=0, le=10000)

    @field_validator("start_time", "end_time")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must include a timezone offset")
        return value.astimezone(IST)

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.start_time <= datetime.now(IST):
            raise ValueError("class must be scheduled in the future")
        return self


class FitnessClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    instructor: str
    start_time: datetime
    end_time: datetime
    capacity: int
    available_slots: int
    created_at: datetime
