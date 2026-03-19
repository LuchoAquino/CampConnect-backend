from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ─── Auth ───────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ─── Profile ─────────────────────────────────────────────
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    university: Optional[str] = None
    student_status: Optional[str] = None   # local | international
    education_level: Optional[str] = None  # licence | master | doctorat | autre
    years_enrolled: Optional[str] = None
    languages: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    activity_types: Optional[List[str]] = None
    onboarding_completed: Optional[bool] = None

class QuizUpdate(BaseModel):
    quiz_data: dict

class ProfileOut(BaseModel):
    id: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    university: Optional[str]
    student_status: Optional[str]
    education_level: Optional[str]
    years_enrolled: Optional[str]
    languages: List[str]
    interests: List[str]
    activity_types: List[str]
    reputation_score: float
    onboarding_completed: bool
    created_at: Optional[datetime]

# ─── Events ──────────────────────────────────────────────
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    location_name: str
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date_start: datetime
    date_end: Optional[datetime] = None
    max_participants: int = 20
    languages: List[str] = ["fr"]
    is_public: bool = True
    poster_url: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    max_participants: Optional[int] = None
    languages: Optional[List[str]] = None
    is_public: Optional[bool] = None
    poster_url: Optional[str] = None
    status: Optional[str] = None

class EventOut(BaseModel):
    id: str
    creator_id: str
    title: str
    description: Optional[str]
    category: str
    location_name: str
    location_address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    date_start: str
    date_end: Optional[str]
    max_participants: int
    current_count: int
    languages: List[str]
    is_public: bool
    poster_url: Optional[str]
    avg_rating: Optional[float]
    status: str
    created_at: str
    spots_left: Optional[int] = None

# ─── Participations ───────────────────────────────────────
class ParticipationOut(BaseModel):
    id: str
    user_id: str
    event_id: str
    status: str
    created_at: str
    profile: Optional[ProfileOut] = None

# ─── Feedback ─────────────────────────────────────────────
class FeedbackCreate(BaseModel):
    rating: int
    feedback_tags: List[str] = []
    comment: Optional[str] = None

class FeedbackOut(BaseModel):
    id: str
    user_id: str
    event_id: str
    rating: int
    feedback_tags: List[str]
    comment: Optional[str]
    created_at: str
