from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Scheme, User, ApplicationTrack
from app.schemas.scheme import RecommendationOut
from app.services.auth_service import get_optional_current_user, get_current_user
from app.recommendation.engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("")
def get_recommendations(
    limit: int = 20,
    category: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Scheme).filter(Scheme.is_active == True)
    if category and category.lower() != "all":
        query = query.filter(Scheme.category.ilike(f"%{category}%"))

    schemes = query.all()
    profile = current_user.profile if current_user else None

    ranked = RecommendationEngine.rank_schemes(
        schemes=schemes,
        profile=profile,
        limit=limit
    )

    # Calculate summary metrics for dashboard
    likely_count = sum(1 for r in ranked if r["eligibility_status"] == "likely_eligible")
    possibly_count = sum(1 for r in ranked if r["eligibility_status"] == "possibly_eligible")
    
    tracked_count = 0
    if current_user:
        tracked_count = db.query(ApplicationTrack).filter(ApplicationTrack.user_id == current_user.id).count()

    completeness = 0
    if profile:
        from app.api.profile import calculate_completeness
        completeness = calculate_completeness(profile)

    return {
        "user_profile": {
            "name": current_user.full_name if current_user else None,
            "occupation": profile.occupation if profile else None,
            "state": profile.state if profile else None,
            "completeness": completeness,
            "is_logged_in": current_user is not None,
            "has_profile": profile is not None
        },
        "stats": {
            "total_recommended": len(ranked),
            "likely_eligible": likely_count,
            "possibly_eligible": possibly_count,
            "applications_tracked": tracked_count,
            "profile_completeness": completeness
        },
        "recommendations": ranked
    }

@router.post("/track")
def track_scheme(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scheme_id = data.get("scheme_id")
    status_val = data.get("status", "Saved")
    notes = data.get("notes")

    if not scheme_id:
        raise HTTPException(status_code=400, detail="scheme_id is required")

    existing = db.query(ApplicationTrack).filter(
        ApplicationTrack.user_id == current_user.id,
        ApplicationTrack.scheme_id == scheme_id
    ).first()

    if existing:
        existing.status = status_val
        if notes:
            existing.notes = notes
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "track_id": existing.id}
    else:
        new_track = ApplicationTrack(
            user_id=current_user.id,
            scheme_id=scheme_id,
            status=status_val,
            notes=notes
        )
        db.add(new_track)
        db.commit()
        db.refresh(new_track)
        return {"status": "created", "track_id": new_track.id}

@router.get("/tracked")
def get_tracked_schemes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tracks = db.query(ApplicationTrack).filter(ApplicationTrack.user_id == current_user.id).all()
    results = []
    for t in tracks:
        results.append({
            "id": t.id,
            "scheme_id": t.scheme.id,
            "scheme_name": t.scheme.name,
            "short_name": t.scheme.short_name,
            "category": t.scheme.category,
            "benefit_amount": t.scheme.benefit_amount,
            "status": t.status,
            "notes": t.notes,
            "applied_date": t.applied_date.strftime("%Y-%m-%d") if t.applied_date else None
        })
    return results
