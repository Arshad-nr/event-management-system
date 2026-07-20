from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, redis_client
from app.core.security import get_current_student_id
from app.schemas.event import (
    EventCreateRequest, EventUpdateRequest, EventResponse,
    PaginatedEventsResponse, EventRegistrationResponse,
)
from app.schemas.student import StudentRegistrationInfo
from app.schemas.common import SuccessResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse)
async def create_event(
    data: EventCreateRequest,
    db: AsyncSession = Depends(get_db),
    student_id: UUID = Depends(get_current_student_id),
):
    event = await event_service.create_event(db, data)
    return EventResponse.model_validate(event, from_attributes=True)


@router.get("/", response_model=PaginatedEventsResponse)
async def get_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await event_service.get_events_paginated(db, redis_client, limit, offset)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    event = await event_service.get_event_by_id(db, event_id)
    return EventResponse.model_validate(event, from_attributes=True)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    data: EventUpdateRequest,
    db: AsyncSession = Depends(get_db),
    student_id: UUID = Depends(get_current_student_id),
):
    event = await event_service.update_event(db, redis_client, event_id, data)
    return EventResponse.model_validate(event, from_attributes=True)


@router.delete("/{event_id}", response_model=SuccessResponse)
async def delete_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    student_id: UUID = Depends(get_current_student_id),
):
    await event_service.delete_event(db, redis_client, event_id)
    return SuccessResponse(message="Event deleted successfully")


@router.post("/{event_id}/register", response_model=EventRegistrationResponse)
async def register_for_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    student_id: UUID = Depends(get_current_student_id),
):
    reg = await event_service.register_for_event(db, redis_client, event_id, student_id)
    return EventRegistrationResponse(
        message="Successfully registered for event",
        event_id=reg.event_id,
        student_id=reg.student_id,
    )


@router.get("/{event_id}/participants", response_model=list[StudentRegistrationInfo])
async def get_event_participants(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    student_id: UUID = Depends(get_current_student_id),
):
    return await event_service.get_event_participants(db, event_id)
