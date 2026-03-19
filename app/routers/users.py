from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ProfileUpdate, QuizUpdate, ProfileOut
from app.db.client import supabase
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(user=Depends(get_current_user)):
    user_id = user["sub"]
    res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return res.data


@router.put("/me", response_model=ProfileOut)
async def update_my_profile(data: ProfileUpdate, user=Depends(get_current_user)):
    user_id = user["sub"]
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = supabase.table("profiles").update(update_data).eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Update failed")
    return res.data[0]


@router.put("/me/quiz", response_model=ProfileOut)
async def submit_quiz(data: QuizUpdate, user=Depends(get_current_user)):
    user_id = user["sub"]
    res = supabase.table("profiles").update({"quiz_data": data.quiz_data}).eq("id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Quiz submission failed")
    return res.data[0]


@router.get("/{user_id}", response_model=ProfileOut)
async def get_user_profile(user_id: str, user=Depends(get_current_user)):
    res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    return res.data


@router.delete("/me")
async def delete_my_account(user=Depends(get_current_user)):
    user_id = user["sub"]
    # Delete profile (cascade deletes participations & feedback)
    supabase.table("profiles").delete().eq("id", user_id).execute()
    # Delete auth user via admin API
    supabase.auth.admin.delete_user(user_id)
    return {"message": "Account deleted successfully"}
