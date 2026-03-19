from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db.client import supabase
from app.dependencies import get_current_user
from app.models.schemas import ParticipationOut

router = APIRouter(prefix="/events", tags=["participations"])


@router.post("/{event_id}/join", status_code=201)
async def join_event(event_id: str, user=Depends(get_current_user)):
    user_id = user["sub"]

    # Check event exists and has space
    event = supabase.table("events").select("*").eq("id", event_id).single().execute()
    if not event.data:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.data["status"] != "active":
        raise HTTPException(status_code=400, detail="Event is not active")
    if event.data["current_count"] >= event.data["max_participants"]:
        raise HTTPException(status_code=400, detail="Event is full")

    # Check not already joined
    existing = (
        supabase.table("participations")
        .select("id")
        .eq("user_id", user_id)
        .eq("event_id", event_id)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=400, detail="Already joined this event")

    res = supabase.table("participations").insert({"user_id": user_id, "event_id": event_id}).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Could not join event")
    return {"message": "Successfully joined the event", "participation": res.data[0]}


@router.delete("/{event_id}/leave", status_code=204)
async def leave_event(event_id: str, user=Depends(get_current_user)):
    user_id = user["sub"]
    res = (
        supabase.table("participations")
        .delete()
        .eq("user_id", user_id)
        .eq("event_id", event_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Participation not found")


@router.get("/{event_id}/participants")
async def list_participants(event_id: str, user=Depends(get_current_user)):
    res = (
        supabase.table("participations")
        .select("*, profile:profiles(id, full_name, avatar_url, university, interests, student_status)")
        .eq("event_id", event_id)
        .eq("status", "confirmed")
        .execute()
    )
    return res.data or []


@router.get("/my/rsvps")
async def my_rsvps(user=Depends(get_current_user)):
    """Return all events the current user has joined."""
    user_id = user["sub"]
    res = (
        supabase.table("participations")
        .select("*, event:events(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return res.data or []
