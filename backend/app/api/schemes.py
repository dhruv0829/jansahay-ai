from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.models.models import Scheme, User
from app.schemas.scheme import SchemeOut, SchemeDetailOut
from app.services.auth_service import get_optional_current_user
from app.eligibility.evaluator import EligibilityEvaluator
from app.recommendation.engine import RecommendationEngine

router = APIRouter(prefix="/schemes", tags=["Schemes"])

@router.get("", response_model=List[SchemeOut])
def list_schemes(
    category: Optional[str] = None,
    state: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "popular",
    db: Session = Depends(get_db)
):
    query = db.query(Scheme).filter(Scheme.is_active == True)

    if category and category.lower() != "all":
        query = query.filter(Scheme.category.ilike(f"%{category}%"))

    if state and state.lower() != "all":
        query = query.filter(
            or_(
                Scheme.applicable_states.ilike("%all%"),
                Scheme.applicable_states.ilike(f"%{state}%")
            )
        )

    if level and level.lower() != "all":
        query = query.filter(Scheme.level.ilike(f"%{level}%"))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Scheme.name.ilike(term),
                Scheme.short_name.ilike(term),
                Scheme.department.ilike(term),
                Scheme.summary.ilike(term),
                Scheme.category.ilike(term)
            )
        )

    schemes = query.all()
    results = []
    for s in schemes:
        s_out = SchemeOut.from_orm(s)
        s_out.benefits_count = len(s.benefits)
        s_out.documents_count = len(s.documents)
        results.append(s_out)

    return results

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
    cat_counts = {}
    for s in schemes:
        cat = s.category
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    categories = [
        {"name": cat, "count": count}
        for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    return categories

@router.get("/{scheme_id_or_slug}")
def get_scheme(
    scheme_id_or_slug: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if scheme_id_or_slug.isdigit():
        scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id_or_slug)).first()
    else:
        scheme = db.query(Scheme).filter(Scheme.slug == scheme_id_or_slug).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    detail = SchemeDetailOut.from_orm(scheme)

    # Attach personalized assessment if user is logged in with profile
    personalized_assessment = None
    if current_user and current_user.profile:
        report = EligibilityEvaluator.evaluate(scheme, current_user.profile)
        rec = RecommendationEngine.score_scheme(scheme, current_user.profile)
        personalized_assessment = {
            "status": report["status"],
            "status_label": report["status_label"],
            "match_score": rec["match_score"],
            "matched_rules": report["matched_rules"],
            "failed_rules": report["failed_rules"],
            "summary_reason": report["summary_reason"],
            "action_tip": report["action_tip"],
            "match_reasons": rec["match_reasons"]
        }

    return {
        "scheme": detail,
        "personalized_assessment": personalized_assessment
    }
