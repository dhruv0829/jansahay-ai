import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.models import User
from app.services.rag_service import JanSahayRAGService
from app.services.chat_service import ChatService

db = SessionLocal()
user = db.query(User).filter(User.email == 'demo@citizen.in').first()

queries = [
    "How can I get ₹5 Lakh hospital insurance under Ayushman Bharat?",
    "What is PM-KISAN and how much financial assistance do farmers receive?",
    "I am a street vendor, can I get a loan without collateral under SVANidhi?",
    "What is the eligibility for Atal Pension Yojana?"
]

for q in queries:
    print("\n" + "="*70)
    print("USER QUERY:", q)
    res = ChatService.generate_response(db, q, user=user)
    print("INTENT:", res["intent"])
    print("CITATIONS:", len(res["citations"]), [c["scheme_name"] for c in res["citations"]])
    print("RESPONSE PREVIEW:\n", res["message"][:280] + "...")
    print("FOLLOW-UP SUGGESTIONS:", res["follow_up_suggestions"][:2])

db.close()
