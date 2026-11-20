import os
import json
import re
from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import (
    Scheme, User, EligibilityRule, SchemeBenefit,
    SchemeDocument, SchemeQA, SchemeConflict, AuditLog
)
from app.schemas.scheme import SchemeOut, SchemeDetailOut
from app.services.auth_service import get_admin_user, get_optional_current_user
from app.database.import_dataset import run_import
from app.services.rag_service import RAGRetriever
from app.schemas.admin import AdminSchemeCreate, AdminUserAccessUpdate

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/stats")
def get_admin_stats(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    total = db.query(Scheme).count()
    verified = db.query(Scheme).filter(Scheme.is_verified == True).count()
    pending = db.query(Scheme).filter(Scheme.is_verified == False).count()
    categories = db.query(Scheme.category).distinct().count()
    users_count = db.query(User).count()
    qa_count = db.query(SchemeQA).count()
    conflict_count = db.query(SchemeConflict).count()

    recent = db.query(Scheme).order_by(Scheme.updated_at.desc()).limit(5).all()
    recent_schemes = [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "last_verified_date": s.last_verified_date,
            "is_verified": s.is_verified
        }
        for s in recent
    ]

    return {
        "total_schemes": total,
        "verified_schemes": verified,
        "pending_verification": pending,
        "total_categories": categories,
        "registered_users": users_count,
        "total_qa_records": qa_count,
        "conflicts_resolved": conflict_count,
        "recent_updates": recent_schemes
    }

@router.get("/quality-metrics")
def get_data_quality_metrics(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Comprehensive Data Quality & Coverage Metrics."""
    schemes = db.query(Scheme).all()
    total = len(schemes)
    if total == 0:
        return {"total_schemes": 0}

    with_urls = sum(1 for s in schemes if s.official_url and "http" in s.official_url)
    with_rules = sum(1 for s in schemes if s.eligibility_rules is not None)
    with_benefits = sum(1 for s in schemes if len(s.benefits) > 0)
    with_docs = sum(1 for s in schemes if len(s.documents) > 0)
    with_qa = sum(1 for s in schemes if len(s.qa_records) > 0)
    with_hindi = sum(1 for s in schemes if s.summary_hindi or s.description_hindi)

    return {
        "total_schemes": total,
        "official_url_coverage": round((with_urls / total) * 100, 1),
        "rule_engine_coverage": round((with_rules / total) * 100, 1),
        "benefits_coverage": round((with_benefits / total) * 100, 1),
        "document_checklist_coverage": round((with_docs / total) * 100, 1),
        "grounded_qa_coverage": round((with_qa / total) * 100, 1),
        "bilingual_hindi_coverage": round((with_hindi / total) * 100, 1),
        "total_qa_pairs": db.query(SchemeQA).count(),
        "total_benefits": db.query(SchemeBenefit).count(),
        "total_documents": db.query(SchemeDocument).count(),
        "dataset_name": "indian_government_schemes_dataset_english_and_hindi.csv"
    }

@router.get("/conflicts")
def get_scheme_conflicts(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Review dataset duplicate variants and conflict resolutions."""
    conflicts = db.query(SchemeConflict).order_by(SchemeConflict.id.asc()).all()
    return [
        {
            "id": c.id,
            "scheme_name": c.scheme_name,
            "variant_name": c.variant_name,
            "conflict_type": c.conflict_type,
            "resolution": c.resolution,
            "status": c.status,
            "details": json.loads(c.details) if c.details else {}
        }
        for c in conflicts
    ]

@router.post("/reimport")
def trigger_dataset_reimport(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to re-run idempotent dataset import and refresh RAG index."""
    report = run_import(recreate=False)
    # Re-initialize RAG index
    RAGRetriever.initialize_index(db)
    return {
        "status": "success",
        "message": "Dataset re-imported successfully and RAG retrieval index reloaded.",
        "report": report
    }

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Retrieve system security and administrative audit trail."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": json.loads(l.details) if l.details else {},
            "timestamp": l.created_at.isoformat()
        }
        for l in logs
    ]

@router.get("/schemes")
def get_admin_schemes(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    schemes = db.query(Scheme).order_by(Scheme.id.asc()).all()
    return [
        {
            "id": s.id,
            "slug": s.slug,
            "name": s.name,
            "short_name": s.short_name,
            "department": s.department,
            "level": s.level,
            "category": s.category,
            "benefit_amount": s.benefit_amount,
            "applicable_states": s.applicable_states,
            "is_verified": s.is_verified,
            "is_active": s.is_active,
            "last_verified_date": s.last_verified_date,
            "benefits_count": len(s.benefits),
            "documents_count": len(s.documents),
            "qa_count": len(s.qa_records)
        }
        for s in schemes
    ]

@router.get("/users")
def get_admin_users(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """List account details needed to manage portal access; never return credentials."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]

@router.patch("/users/{user_id}/access")
def update_user_access(
    user_id: int,
    update: AdminUserAccessUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Grant/revoke admin access or activate/deactivate a user account."""
    changes = update.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide is_admin and/or is_active.")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot change your own administrator access or account status.")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    removes_active_admin = target.is_admin and target.is_active and (
        changes.get("is_admin") is False or changes.get("is_active") is False
    )
    if removes_active_admin:
        other_active_admin = db.query(User).filter(
            User.is_admin == True,
            User.is_active == True,
            User.id != target.id,
        ).first()
        if not other_active_admin:
            raise HTTPException(status_code=400, detail="The last active administrator cannot be removed or deactivated.")

    before = {"is_admin": target.is_admin, "is_active": target.is_active}
    for field, value in changes.items():
        setattr(target, field, value)
    after = {"is_admin": target.is_admin, "is_active": target.is_active}
    db.add(AuditLog(
        user_id=current_user.id,
        action="USER_ACCESS_UPDATED",
        entity_type="User",
        entity_id=str(target.id),
        details=json.dumps({"email": target.email, "before": before, "after": after}),
    ))
    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "email": target.email,
        "full_name": target.full_name,
        "is_active": target.is_active,
        "is_admin": target.is_admin,
        "message": "User access updated.",
    }

@router.post("/schemes/{scheme_id}/verify")
def toggle_scheme_verification(
    scheme_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    scheme.is_verified = not scheme.is_verified
    scheme.last_verified_date = date.today().isoformat() if scheme.is_verified else None
    # Only verified schemes should enter public discovery and recommendations.
    scheme.is_active = scheme.is_verified
    db.commit()
    db.refresh(scheme)
    return {
        "id": scheme.id,
        "is_verified": scheme.is_verified,
        "last_verified_date": scheme.last_verified_date,
        "message": f"Verification status updated to {'Verified' if scheme.is_verified else 'Unverified'}"
    }

@router.post("/schemes")
def create_scheme(
    data: AdminSchemeCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    payload = data.model_dump()
    slug = re.sub(r"[^a-z0-9]+", "-", payload["name"].lower()).strip("-")[:140]
    if not slug:
        slug = f"scheme-{db.query(Scheme).count() + 1}"
    existing = db.query(Scheme).filter(Scheme.slug == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="A scheme with this name already exists.")

    scheme = Scheme(
        slug=slug,
        **payload,
        is_active=False,
        is_verified=False,
        last_verified_date=None
    )
    db.add(scheme)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="SCHEME_CREATED",
        entity_type="Scheme",
        entity_id=str(scheme.id),
        details=json.dumps({"name": scheme.name, "slug": scheme.slug}),
    ))
    db.commit()
    db.refresh(scheme)
    return {"message": "Scheme created successfully", "scheme_id": scheme.id, "slug": scheme.slug}
