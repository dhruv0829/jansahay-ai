import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.models import Scheme

db = SessionLocal()
for kw in ['kisan', 'pension', 'sukanya', 'ayushman']:
    for s in db.query(Scheme).all():
        if kw in s.name.lower() or kw in s.slug.lower():
            print(f"id={s.id} | slug='{s.slug}' | name='{s.name}'")
db.close()
