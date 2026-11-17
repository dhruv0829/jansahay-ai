import os
import sys
import pytest

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.models import Scheme
from app.eligibility.evaluator import EligibilityEvaluator

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_pm_kisan_eligible_farmer(db):
    pm_kisan = db.query(Scheme).filter(Scheme.slug == "pm-kisan").first()
    assert pm_kisan is not None

    profile = {
        "age": 35,
        "gender": "Male",
        "state": "Maharashtra",
        "occupation": "Farmer",
        "annual_income": 180000.0,
        "landholding_acres": 2.5,
        "social_category": "OBC"
    }

    report = EligibilityEvaluator.evaluate(pm_kisan, profile)
    assert report["status"] == EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE
    assert "Likely eligible" in report["status_label"]
    assert len(report["unmet_criteria"]) == 0
    assert any("Landholding verified" in m or "acres" in m for m in report["satisfied_criteria"])
    assert report["score"] >= 85

def test_pm_kisan_ineligible_due_to_no_land(db):
    pm_kisan = db.query(Scheme).filter(Scheme.slug == "pm-kisan").first()
    assert pm_kisan is not None

    profile = {
        "age": 35,
        "gender": "Male",
        "state": "Maharashtra",
        "occupation": "Farmer",
        "annual_income": 180000.0,
        "landholding_acres": 0.0, # No land
        "social_category": "General"
    }

    report = EligibilityEvaluator.evaluate(pm_kisan, profile)
    assert report["status"] == EligibilityEvaluator.STATUS_CONDITIONS_NOT_MET
    assert len(report["unmet_criteria"]) >= 1
    assert any("land" in u.lower() for u in report["unmet_criteria"])

def test_pm_kisan_missing_income_returns_more_info_required(db):
    pm_kisan = db.query(Scheme).filter(Scheme.slug == "pm-kisan").first()
    assert pm_kisan is not None

    # Missing income and landholding
    profile = {
        "age": 35,
        "gender": "Male",
        "state": "Maharashtra",
        "occupation": "Farmer",
        "annual_income": None, # Unknown
        "landholding_acres": None, # Unknown
        "social_category": "General"
    }

    report = EligibilityEvaluator.evaluate(pm_kisan, profile)
    assert report["status"] == EligibilityEvaluator.STATUS_MORE_INFO_REQUIRED
    assert len(report["unknown_criteria"]) >= 1
    assert len(report["follow_up_questions"]) >= 1

def test_atal_pension_yojana_age_boundaries(db):
    apy = db.query(Scheme).filter(Scheme.slug == "atal-pension-yojana").first()
    assert apy is not None

    # Exact boundary 18 (min_age) -> Likely eligible
    profile_18 = {"age": 18, "gender": "Female", "state": "Karnataka", "occupation": "Self-Employed"}
    r18 = EligibilityEvaluator.evaluate(apy, profile_18)
    assert r18["status"] == EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE

    # Exact boundary 40 (max_age) -> Likely eligible
    profile_40 = {"age": 40, "gender": "Male", "state": "Karnataka", "occupation": "Citizen"}
    r40 = EligibilityEvaluator.evaluate(apy, profile_40)
    assert r40["status"] == EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE

    # Over boundary 41 (exceeds max_age) -> conditions_not_met
    profile_41 = {"age": 41, "gender": "Male", "state": "Karnataka", "occupation": "Citizen"}
    r41 = EligibilityEvaluator.evaluate(apy, profile_41)
    assert r41["status"] == EligibilityEvaluator.STATUS_CONDITIONS_NOT_MET
    assert any("41" in u and "outside" in u for u in r41["unmet_criteria"])

def test_sukanya_samriddhi_gender_restriction(db):
    ssy = db.query(Scheme).filter(Scheme.slug == "sukanya-samriddhi-yojana").first()
    assert ssy is not None

    # Male profile -> conditions_not_met
    profile_male = {"age": 6, "gender": "Male", "state": "Delhi"}
    r_male = EligibilityEvaluator.evaluate(ssy, profile_male)
    assert r_male["status"] == EligibilityEvaluator.STATUS_CONDITIONS_NOT_MET
    assert any("Female" in u or "beneficiaries" in u for u in r_male["unmet_criteria"])

    # Female child age 6 -> Likely eligible
    profile_female = {"age": 6, "gender": "Female", "state": "Delhi"}
    r_female = EligibilityEvaluator.evaluate(ssy, profile_female)
    assert r_female["status"] == EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE

def test_no_profile_handles_safely(db):
    pm_kisan = db.query(Scheme).filter(Scheme.slug == "pm-kisan").first()
    report = EligibilityEvaluator.evaluate(pm_kisan, None)
    assert report["status"] == EligibilityEvaluator.STATUS_MORE_INFO_REQUIRED
    assert len(report["follow_up_questions"]) > 0
    assert "disclaimer" in report
