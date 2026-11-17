import os
import json
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
    data: dict,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    slug = data.get("slug") or data.get("name", "").lower().replace(" ", "-")[:40]
    existing = db.query(Scheme).filter(Scheme.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(db.query(Scheme).count()) + 1}"

    scheme = Scheme(
        slug=slug,
        name=data.get("name"),
        short_name=data.get("short_name"),
        department=data.get("department", "Ministry of Public Welfare"),
        ministry=data.get("ministry", "Government of India"),
        level=data.get("level", "Central"),
        applicable_states=data.get("applicable_states", "All"),
        category=data.get("category", "Social Welfare"),
        summary=data.get("summary", ""),
        description=data.get("description", ""),
        target_beneficiary=data.get("target_beneficiary", "Eligible Citizens"),
        benefit_type=data.get("benefit_type", "Financial Assistance"),
        benefit_amount=data.get("benefit_amount", "As per norms"),
        application_mode=data.get("application_mode", "Online"),
        official_url=data.get("official_url", "https://www.india.gov.in"),
        is_active=True,
        is_verified=False,
        last_verified_date=None
    )
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return {"message": "Scheme created successfully", "scheme_id": scheme.id, "slug": scheme.slug}
