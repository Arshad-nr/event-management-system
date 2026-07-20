import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class EventCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    date: datetime
    location: str | None = None
    max_capacity: int = Field(gt=0)

class EventUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    date: datetime | None = None
    location: str | None = None
    max_capacity: int | None = Field(None, gt=0)

class EventResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    date: datetime
    location: str | None
    max_capacity: int
    current_registered: int

    model_config = ConfigDict(from_attributes=True)

class PaginatedEventsResponse(BaseModel):
    success: bool = True
    data: list[EventResponse]
    limit: int
    offset: int
    total: int

class EventRegistrationResponse(BaseModel):
    success: bool = True
    message: str
    event_id: uuid.UUID
    student_id: uuid.UUID
