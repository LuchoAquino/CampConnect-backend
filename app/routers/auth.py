from fastapi import APIRouter, HTTPException
from app.models.schemas import UserRegister, UserLogin
from app.db.client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(data: UserRegister):
    """Register a new user with Supabase Auth."""
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"full_name": data.full_name}},
        })
        if res.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")
        return {"message": "Registration successful. Please verify your email.", "user_id": res.user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(data: UserLogin):
    """Log in and return Supabase session tokens."""
    try:
        res = supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
        if res.session is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "user": {"id": res.user.id, "email": res.user.email},
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh an expired access token."""
    try:
        res = supabase.auth.refresh_session(refresh_token)
        return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
