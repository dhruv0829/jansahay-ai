import os
import sys
import pytest

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.main import health_check, root
from app.api.schemes import list_schemes, get_categories, get_scheme
from app.api.recommendations import get_recommendations
from app.api.chat import handle_chat_message
from app.api.admin import get_admin_stats, get_data_quality_metrics, get_scheme_conflicts
from app.schemas.chat import ChatRequest, ChatResponse

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert res["database"] == "connected"

def test_root_endpoint():
    res = root()
    assert res["status"] == "online"
    assert res["portal_name"] == "JanSahay"

def test_list_schemes_api(db):
    schemes = list_schemes(db=db)
    assert isinstance(schemes, list)
    assert len(schemes) >= 70
    assert any(s.category == "Agriculture" for s in schemes)

def test_schemes_categories_api(db):
    cats = get_categories(db=db)
    assert isinstance(cats, list)
    assert any(c["name"] == "Agriculture" for c in cats)
    assert any(c["name"] == "Healthcare" for c in cats)

def test_scheme_detail_by_slug_api(db):
    data = get_scheme("pm-kisan", current_user=None, db=db)
    assert "scheme" in data
    assert data["scheme"].name == "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
    assert data["scheme"].official_url == "https://pmkisan.gov.in"
    assert len(data["scheme"].benefits) >= 1
    assert len(data["scheme"].documents) >= 1

def test_recommendations_endpoint_api(db):
    data = get_recommendations(limit=10, current_user=None, db=db)
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert "stats" in data

def test_chat_endpoint_api(db):
    req = ChatRequest(
        message="Which healthcare schemes provide cashless hospital cover?",
        session_id="test-session",
        language="en"
    )
    res = handle_chat_message(req, current_user=None, db=db)
    assert res["message"] is not None
    assert len(res["citations"]) > 0
    assert any("pmjay.gov.in" in c["official_url"] for c in res["citations"])

    # Verify Pydantic serialization used by FastAPI response pipeline
    chat_response = ChatResponse(**res)
    json_dump = chat_response.model_dump(mode="json")
    assert "recommended_schemes" in json_dump
    if json_dump["recommended_schemes"]:
        assert isinstance(json_dump["recommended_schemes"][0]["scheme"], dict)
        assert "name" in json_dump["recommended_schemes"][0]["scheme"]

def test_chat_greeting_serialization(db):
    req = ChatRequest(message="Namaste", session_id="greet-session")
    res = handle_chat_message(req, current_user=None, db=db)
    assert res["intent"] == "greeting"
    chat_response = ChatResponse(**res)
    json_dump = chat_response.model_dump(mode="json")
    assert len(json_dump["recommended_schemes"]) == 3
    assert isinstance(json_dump["recommended_schemes"][0]["scheme"], dict)

def test_admin_stats_and_quality_api(db):
    stats = get_admin_stats(db=db)
    assert stats["total_schemes"] >= 70
    assert stats["total_qa_records"] == 3473

    qual = get_data_quality_metrics(db=db)
    assert qual["official_url_coverage"] == 100.0
    assert qual["total_qa_pairs"] == 3473

def test_admin_conflicts_api(db):
    conflicts = get_scheme_conflicts(db=db)
    assert isinstance(conflicts, list)
    assert len(conflicts) > 0
