from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db.client import supabase
from app.dependencies import get_current_user
from app.models.schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/events", tags=["feedback"])

@router.post("/{event_id}/feedback", response_model=FeedbackOut, status_code=201)
async def submit_feedback(event_id: str, data: FeedbackCreate, user=Depends(get_current_user)):
    user_id = user["sub"]

    # Verify the user participated in this event
    participation = (
        supabase.table("participations")
        .select("id")
        .eq("user_id", user_id)
        .eq("event_id", event_id)
        .execute()
    )
    if not participation.data:
        raise HTTPException(status_code=403, detail="You did not participate in this event")

    # Check for duplicate feedback
    existing = (
        supabase.table("event_feedback")
        .select("id")
        .eq("user_id", user_id)
        .eq("event_id", event_id)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=400, detail="You already submitted feedback for this event")

    feedback = {"user_id": user_id, "event_id": event_id, **data.model_dump()}
    res = supabase.table("event_feedback").insert(feedback).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Feedback submission failed")
    return res.data[0]


@router.get("/{event_id}/feedback", response_model=List[FeedbackOut])
async def get_event_feedback(event_id: str, user=Depends(get_current_user)):
    res = supabase.table("event_feedback").select("*").eq("event_id", event_id).execute()
    return res.data or []