from fastapi import APIRouter, Depends
from typing import List
from app.db.client import supabase
from app.dependencies import get_current_user
from app.models.schemas import EventOut
from datetime import datetime, timezone

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

CATEGORY_SCORE_MAP = {
    "sport":      {"sport": 1.0, "social": 0.3, "autre": 0.2},
    "culture":    {"culture": 1.0, "academic": 0.4, "social": 0.3},
    "social":     {"social": 1.0, "sport": 0.4, "networking": 0.4},
    "academic":   {"academic": 1.0, "culture": 0.3, "networking": 0.2},
    "networking": {"networking": 1.0, "social": 0.4, "academic": 0.3},
    "autre":      {"autre": 1.0},
}


def compute_score(event: dict, profile: dict) -> float:
    score = 0.0

    user_interests = set(profile.get("interests", []) + profile.get("activity_types", []))
    event_cat = event.get("category", "")
    cat_map = CATEGORY_SCORE_MAP.get(event_cat, {})
    interest_score = max((cat_map.get(i, 0.0) for i in user_interests), default=0.0)
    score += interest_score * 0.4

    user_langs = set(profile.get("languages", ["fr"]))
    event_langs = set(event.get("languages", ["fr"]))
    lang_score = 1.0 if user_langs & event_langs else 0.0
    score += lang_score * 0.2

    max_p = event.get("max_participants", 1)
    cur = event.get("current_count", 0)
    popularity = min(cur / max_p, 1.0) if max_p > 0 else 0.0
    score += popularity * 0.2

    try:
        date_start = datetime.fromisoformat(event["date_start"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_away = max((date_start - now).days, 0)
        recency = max(1.0 - days_away / 30.0, 0.0)
    except Exception:
        recency = 0.5
    score += recency * 0.2

    return round(score, 4)


@router.get("", response_model=List[EventOut])
async def get_recommendations(user=Depends(get_current_user)):
    user_id = user["sub"]

    profile_res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    profile = profile_res.data or {}

    now_iso = datetime.now(timezone.utc).isoformat()
    events_res = (
        supabase.table("events")
        .select("*")
        .eq("is_public", True)
        .eq("status", "active")
        .gte("date_start", now_iso)
        .execute()
    )
    all_events = events_res.data or []

    parts_res = (
        supabase.table("participations")
        .select("event_id")
        .eq("user_id", user_id)
        .execute()
    )
    joined_ids = {p["event_id"] for p in (parts_res.data or [])}

    scored = []
    for e in all_events:
        if e["id"] in joined_ids:
            continue
        e["spots_left"] = e["max_participants"] - e["current_count"]
        e["_score"] = compute_score(e, profile)
        scored.append(e)

    scored.sort(key=lambda x: x["_score"], reverse=True)
    
    for e in scored:
        e.pop("_score", None)

    return scored[:20]