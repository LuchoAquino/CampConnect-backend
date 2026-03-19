from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from app.models.schemas import EventCreate, EventUpdate, EventOut
from app.db.client import supabase
from app.dependencies import get_current_user
from app.services.poster_generator import generate_and_upload_poster
from datetime import datetime

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[EventOut])
async def list_events(
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    max_people: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    offset: int = Query(0),
):
    """List public events with optional filters."""
    query = (
        supabase.table("events")
        .select("*")
        .eq("is_public", True)
        .eq("status", "active")
    )
    if category:
        query = query.eq("category", category)
    if date_from:
        query = query.gte("date_start", date_from)
    if date_to:
        query = query.lte("date_start", date_to)
    if max_people:
        query = query.lte("max_participants", max_people)
    if search:
        query = query.ilike("title", f"%{search}%")

    query = query.order("date_start").range(offset, offset + limit - 1)
    res = query.execute()

    events = []
    for e in (res.data or []):
        e["spots_left"] = e["max_participants"] - e["current_count"]
        events.append(e)
    return events


@router.post("", response_model=EventOut, status_code=201)
async def create_event(data: EventCreate, user=Depends(get_current_user)):
    user_id = user["sub"]
    event_data = data.model_dump()
    # Convert datetime objects to ISO strings
    for k, v in event_data.items():
        if isinstance(v, datetime):
            event_data[k] = v.isoformat()
            
    # Auto-generate poster if not provided
    if not event_data.get("poster_url"):
        auto_url = generate_and_upload_poster(
            title=event_data["title"],
            category=event_data["category"],
            date_str=event_data["date_start"],
            location=event_data["location_name"],
            description=event_data.get("description", "")
        )
        event_data["poster_url"] = auto_url

    event_data["creator_id"] = user_id
    res = supabase.table("events").insert(event_data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Event creation failed")
    e = res.data[0]
    e["spots_left"] = e["max_participants"] - e["current_count"]
    return e


@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: str):
    res = supabase.table("events").select("*").eq("id", event_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Event not found")
    e = res.data
    e["spots_left"] = e["max_participants"] - e["current_count"]
    return e


@router.put("/{event_id}", response_model=EventOut)
async def update_event(event_id: str, data: EventUpdate, user=Depends(get_current_user)):
    user_id = user["sub"]
    # Verify ownership
    check = supabase.table("events").select("creator_id").eq("id", event_id).single().execute()
    if not check.data or check.data["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this event")

    update_data = data.model_dump(exclude_none=True)
    for k, v in update_data.items():
        if isinstance(v, datetime):
            update_data[k] = v.isoformat()

    res = supabase.table("events").update(update_data).eq("id", event_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Update failed")
    e = res.data[0]
    e["spots_left"] = e["max_participants"] - e["current_count"]
    return e


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str, user=Depends(get_current_user)):
    user_id = user["sub"]
    check = supabase.table("events").select("creator_id").eq("id", event_id).single().execute()
    if not check.data or check.data["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")
    supabase.table("events").delete().eq("id", event_id).execute()
