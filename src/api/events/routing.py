from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from api.db.session import get_session

from sqlalchemy import func, case
from datetime import datetime, timedelta, timezone
from timescaledb.hyperfunctions import time_bucket

from .models import (
    EventModel, 
    EventListSchema, 
    EventCreateSchema,
    # EventUpdateSchema,
    EventBucketSchema,
    get_utc_now,
    )
from api.db.db_config import DATABASE_URL

router = APIRouter()

DEFAULT_LOOKUP_PAGES = ['/about', '/contact', '/pages', '/pricing', 'pricing']

@router.get('/', response_model=List[EventBucketSchema])
def read_events(
        duration: str = Query(default='1 day'),
        pages: List = Query(default=None),
        session: Session = Depends(get_session),
    ):
    os_case = case(
        (EventModel.user_agent.ilike("%windows%"), 'Windows'),
        (EventModel.user_agent.ilike("%macintosh%"), 'Macbook'),
        (EventModel.user_agent.ilike("%iphone%"), 'iOS'),
        (EventModel.user_agent.ilike("%android%"), 'Android'),
        (EventModel.user_agent.ilike("%linux%"), 'Linux'),
        else_='Other'
    ).label('operating_system')
    # query = select(EventModel).order_by(EventModel.updated_at.asc()).limit(10)
    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = pages if isinstance(pages, List) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES
    # start = datetime.now(timezone.utc) - timedelta(hours=1)
    # finish = datetime.now(timezone.utc) - timedelta(seconds=278, milliseconds=600)
    query = (
        select(
            bucket.label('bucket'),
            os_case,
            EventModel.page.label('page'),
            func.avg(EventModel.duration).label('avg_duration'),
            func.count().label('count')
        ).where(
            EventModel.page.in_(lookup_pages)
        ).group_by(
            bucket,
            os_case,
            EventModel.page,
        ).order_by(
            bucket,
            os_case,
            EventModel.page
        )
        )
    results = session.exec(query).fetchall()
    return results


@router.post('/', response_model = EventModel)
def create_event(
        payload:EventCreateSchema,
        session: Session = Depends(get_session)):
    data = payload.model_dump()
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get('/{event_id}', response_model=EventModel)
def get_events(event_id:int, session: Session = Depends(get_session)):
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail='Event not found...')
    return result


# @router.put('/{event_id}', response_model=EventModel)
# def update_events(
#         event_id:int,
#         payload:EventUpdateSchema,
#         session: Session = Depends(get_session)
#         ):
#     query = select(EventModel).where(EventModel.id == event_id)
#     obj = session.exec(query).first()
#     if not obj:
#         raise HTTPException(status_code=404, detail='Event not found...')
#     data = payload.model_dump(exclude_unset=True)
#     for k,v in data.items():
#         setattr(obj, k, v)
#     obj.updated_at = get_utc_now()
#     session.add(obj)
#     session.commit()
#     session.refresh(obj)
#     return obj

@router.delete('/{event_id}')
def delete_event(event_id:int, session: Session = Depends(get_session)):
    query = select(EventModel).where(EventModel.id == event_id)
    obj = session.exec(query).first()
    if not obj:
        raise HTTPException(status_code=404, detail='Event not found...')
    session.delete(obj)
    session.commit()
    return {'status': 'Success', 'message': 'Event removed successfully'}