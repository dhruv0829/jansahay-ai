from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, UserProfile
from app.schemas.profile import ProfileUpdate, ProfileOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/profile", tags=["User Profile"])

def calculate_completeness(p: UserProfile) -> int:
    fields = [
        p.age, p.gender, p.state, p.district, p.occupation,
        p.annual_income, p.social_category
    ]
    filled = sum(1 for f in fields if f is not None and str(f).strip() != "")
    # Add bonus for rural/landholding if applicable
    if p.is_rural is not None:
        filled += 1
    total = len(fields) + 1
    return int((filled / total) * 100)

@router.get("", response_model=ProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding."
        )
    
    out = ProfileOut.from_orm(profile)
    out.completeness_percentage = calculate_completeness(profile)
    return out

@router.put("", response_model=ProfileOut)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    out = ProfileOut.from_orm(profile)
    out.completeness_percentage = calculate_completeness(profile)
    return out
