import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.models import Scheme, User
from app.recommendation.engine import RecommendationEngine
from app.schemas.scheme import RecommendationOut, SchemeDetailOut, SchemeOut

db = SessionLocal()
schemes = db.query(Scheme).all()
user = db.query(User).filter(User.email == 'demo@citizen.in').first()

print(f"Total schemes in database: {len(schemes)}")
print(f"Demo citizen: {user.full_name}, Occupation: {user.profile.occupation}, State: {user.profile.state}")

ranked = RecommendationEngine.rank_schemes(schemes, user.profile, limit=5)
print(f"Total top recommendations: {len(ranked)}")

for i, r in enumerate(ranked):
    s = r['scheme']
    print(f"{i+1}. {s.name} ({s.category})")
    print(f"   Match Score: {r['match_score']}% | Status: {r['status_label']}")
    print(f"   Reasons: {r['match_reasons']}")
    
    # Test Pydantic model validation
    s_detail = SchemeDetailOut.model_validate(s)
    rec_out = RecommendationOut(
        scheme=s_detail,
        match_score=r['match_score'],
        eligibility_status=r['eligibility_status'],
        status_label=r['status_label'],
        match_reasons=r['match_reasons'],
        missing_criteria=r['missing_criteria'],
        score_breakdown=r['score_breakdown']
    )

print("\nPydantic validation of all 5 recommendations succeeded flawlessly!")

# Test categories
categories = db.query(Scheme.category).distinct().all()
print(f"Distinct categories ({len(categories)}): {[c[0] for c in categories]}")

# Test Q&A records
from app.models.models import SchemeQA
qa_count = db.query(SchemeQA).count()
print(f"Total Q&A records in scheme_qa table: {qa_count}")

db.close()
