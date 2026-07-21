import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import Event, EventRegistration, Student
from app.schemas.event import EventCreateRequest, EventUpdateRequest
from app.services.exceptions import EventNotFoundException, EventFullException, AlreadyRegisteredException
from app.services.cache_service import get_cached_events, set_cached_events, invalidate_events_cache, EVENTS_CACHE_PREFIX, acquire_lock, release_lock
async def create_event(db: AsyncSession, data: EventCreateRequest) -> Event:
    new_event = Event(**data.model_dump())
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event

async def get_events_paginated(db: AsyncSession, redis, limit: int, offset: int) -> dict:
    cache_key = f"{EVENTS_CACHE_PREFIX}{limit}:{offset}"
    lock_key = f"lock:{cache_key}"
    
    cached_data = await get_cached_events(redis, cache_key)
    if cached_data:
        return cached_data

    # Cache miss. Try to acquire the Redis lock.
    acquired = await acquire_lock(redis, lock_key, ttl=10)
    
    if not acquired:
        # Someone else holds the lock. Wait and poll the cache.
        for _ in range(10): # wait up to 1 second
            await asyncio.sleep(0.1)
            cached_data = await get_cached_events(redis, cache_key)
            if cached_data:
                return cached_data

    try:
        # Double check cache inside lock (in case populated while waiting)
        cached_data = await get_cached_events(redis, cache_key)
        if cached_data:
            return cached_data

        result = await db.execute(select(Event).limit(limit).offset(offset))
        events = result.scalars().all()

        count_result = await db.execute(select(func.count(Event.id)))
        total = count_result.scalar_one()

        # Convert events to dict for JSON serialization
        events_data = [
            {
                "id": str(e.id),
                "title": e.title,
                "description": e.description,
                "date": e.date.isoformat() if e.date else None,
                "location": e.location,
                "max_capacity": e.max_capacity,
                "current_registered": e.current_registered,
            }
            for e in events
        ]

        response_data = {
            "data": events_data,
            "limit": limit,
            "offset": offset,
            "total": total
        }

        await set_cached_events(redis, cache_key, response_data)
        return response_data
    finally:
        if acquired:
            await release_lock(redis, lock_key)

async def get_event_by_id(db: AsyncSession, event_id: UUID) -> Event:
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalars().first()
    if not event:
        raise EventNotFoundException()
    return event

async def update_event(db: AsyncSession, redis, event_id: UUID, data: EventUpdateRequest) -> Event:
    event = await get_event_by_id(db, event_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    await db.commit()
    await db.refresh(event)
    await invalidate_events_cache(redis)
    return event

async def delete_event(db: AsyncSession, redis, event_id: UUID) -> None:
    event = await get_event_by_id(db, event_id)
    await db.delete(event)
    await db.commit()
    await invalidate_events_cache(redis)

async def register_for_event(db: AsyncSession, redis, event_id: UUID, student_id: UUID) -> EventRegistration:
    result = await db.execute(
        select(Event).where(Event.id == event_id).with_for_update()
    )
    event = result.scalars().first()
    if not event:
        raise EventNotFoundException()

    reg_result = await db.execute(
        select(EventRegistration)
        .where(EventRegistration.event_id == event_id)
        .where(EventRegistration.student_id == student_id)
    )
    if reg_result.scalars().first():
        raise AlreadyRegisteredException()

    if event.current_registered >= event.max_capacity:
        raise EventFullException()

    event.current_registered += 1
    new_reg = EventRegistration(event_id=event_id, student_id=student_id)
    db.add(new_reg)
    await db.commit()
    await db.refresh(new_reg)
    
    await invalidate_events_cache(redis)
    return new_reg

async def get_event_participants(db: AsyncSession, event_id: UUID) -> list:
    event = await get_event_by_id(db, event_id)
    
    result = await db.execute(
        select(Student, EventRegistration.registered_at)
        .join(EventRegistration, Student.id == EventRegistration.student_id)
        .where(EventRegistration.event_id == event_id)
    )
    
    participants = []
    for student, registered_at in result.all():
        participants.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "registered_at": registered_at
        })
    
    return participants

