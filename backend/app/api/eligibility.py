from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Scheme, User
from app.schemas.eligibility import EligibilityCheckRequest, SchemeEligibilityReport
from app.services.auth_service import get_optional_current_user
from app.eligibility.evaluator import EligibilityEvaluator

router = APIRouter(prefix="/eligibility", tags=["Eligibility Checker"])

@router.post("/check", response_model=SchemeEligibilityReport)
def check_eligibility(
    req: EligibilityCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not req.scheme_id:
        raise HTTPException(status_code=400, detail="scheme_id is required")

    scheme = db.query(Scheme).filter(Scheme.id == req.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    profile_data = None
    if req.profile:
        profile_data = req.profile.dict()
    elif current_user and current_user.profile:
        profile_data = current_user.profile

    report = EligibilityEvaluator.evaluate(scheme, profile_data)
    return report
