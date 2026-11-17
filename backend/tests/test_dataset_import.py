import os
import sys
import json
import pytest

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.models import Scheme, SchemeQA, SchemeConflict, EligibilityRule, SchemeBenefit, SchemeDocument
from app.database.import_dataset import run_import, DATASET_PATH, RAW_TO_CANONICAL

def test_dataset_exists():
    assert os.path.exists(DATASET_PATH), f"Real dataset must exist at {DATASET_PATH}"
    size_mb = os.path.getsize(DATASET_PATH) / (1024 * 1024)
    assert size_mb > 15.0, f"Real dataset should be >15MB (got {size_mb:.2f}MB)"

def test_database_populated_from_real_dataset():
    db = SessionLocal()
    try:
        schemes = db.query(Scheme).all()
        # Ensure production catalog has all 73 canonical schemes
        assert len(schemes) >= 70, f"Expected at least 70 canonical schemes, found {len(schemes)}"
        
        # Verify 3473 Q&A rows
        qa_count = db.query(SchemeQA).count()
        assert qa_count == 3473, f"Expected exactly 3473 Q&A records, found {qa_count}"
        
        # Verify benefits and documents are populated
        benefit_count = db.query(SchemeBenefit).count()
        doc_count = db.query(SchemeDocument).count()
        assert benefit_count >= 70, f"Expected benefits populated, got {benefit_count}"
        assert doc_count >= 150, f"Expected documents populated, got {doc_count}"
    finally:
        db.close()

def test_deduplication_and_conflicts_preserved():
    db = SessionLocal()
    try:
        conflicts = db.query(SchemeConflict).all()
        assert len(conflicts) > 0, "Conflicts table must preserve merged variants for audit"
        
        # Verify canonical schemes exist without duplicate variants in production
        slugs = [s.slug for s in db.query(Scheme).all()]
        assert len(slugs) == len(set(slugs)), "All scheme slugs in production must be unique"
        
        # Verify specific merged variants
        conflict_variants = [c.variant_name for c in conflicts]
        assert "PM-KISAN" in conflict_variants or "PM Kisan Samman Nidhi" in conflict_variants
        assert "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)" in conflict_variants
    finally:
        db.close()

def test_no_mock_data_in_production():
    db = SessionLocal()
    try:
        # Verify all schemes have source dataset marked
        schemes = db.query(Scheme).all()
        for s in schemes:
            assert s.source_dataset == "indian_government_schemes_dataset_english_and_hindi.csv"
            assert s.official_url and s.official_url.startswith("http")
            assert s.summary and len(s.summary) > 20
    finally:
        db.close()
