# JanSahay Backend Engine

The backend for **JanSahay** is implemented in **FastAPI (Python 3.10+)** with **SQLAlchemy** and a rule-based eligibility evaluation and transparent multi-criteria recommendation engine.

## Key Features

1. **Rule-Based Eligibility Engine** (`app/eligibility/evaluator.py`):
   - Computes deterministic boolean and weighted criteria checks: Age, Gender, State, Occupation, Income Ceiling, Landholding, Rural/Urban status, BPL card, and Disability status.
   - Generates exact human-readable reasons for matched rules and disqualifying grounds.

2. **Transparent Multi-Criteria Recommendation Algorithm** (`app/recommendation/engine.py`):
   - Weighted scoring:
     - Eligibility Rules Match: 40%
     - Location Match: 20%
     - Occupation Match: 15%
     - Income Relevance: 10%
     - Social Category: 10%
     - Context / Intent: 5%

3. **Pluggable AI Scheme Assistant** (`app/services/chat_service.py`):
   - Real-time intent classification for Agriculture, Healthcare, Housing, Education, Entrepreneurship, Women & Child, and Social Security.
   - Cross-references user profile demographics with schemes to return structured scheme cards.
   - Explainability logic responding directly to questions like *"Why am I eligible for this scheme?"*.

4. **Zero-Friction Database Setup**:
   - Runs out-of-the-box on SQLite (`jansahay.db`) with automatic self-seeding on initial startup.
   - PostgreSQL ready via standard SQLAlchemy connection strings.

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database seed (optional: backend auto-seeds on first launch)
python -m app.database.seed

# 3. Start development server
uvicorn app.main:app --reload --port 8000
```

The interactive API documentation is accessible at `http://127.0.0.1:8000/docs`.

## Supabase PostgreSQL

The backend uses two logical schemas in the same Supabase PostgreSQL database:

- `schemes`: scheme catalog, eligibility rules, benefits, scheme documents, Q&A, and conflict records.
- `credentials`: accounts, profiles, applications, uploaded-document metadata, audit logs, and chat history.

Copy the repository `.env.example` to `backend/.env`, then set `DATABASE_URL` to the SQLAlchemy form of the Session Pooler URL from the Supabase **Connect** dialog. Keep the password URL-encoded and use `?sslmode=require`. Keep `backend/.env` private; it is excluded by `.gitignore`. The backend keeps using JanSahay's existing FastAPI authentication. A Supabase publishable key is not a PostgreSQL connection string.

Install the backend requirements, including the PostgreSQL driver:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To copy an existing SQLite database, first run a read-only dry run and inspect the row counts:

```powershell
python migrate_sqlite_to_supabase.py
```

Only apply the migration after confirming the destination is the intended empty Supabase database:

```powershell
python migrate_sqlite_to_supabase.py --apply
```

The migration preserves user IDs and password hashes, refuses to merge into a populated destination, records a completion marker, and verifies row counts. It migrates uploaded-document metadata only; locally stored document files need a separate storage migration. Startup seeding and Admin re-sync leave a populated database unchanged. Destructive recreation is refused for PostgreSQL.

## Production configuration

Set `APP_ENV=production`, a unique `SECRET_KEY` of at least 32 characters, and `CORS_ALLOWED_ORIGINS` to the exact frontend origin(s). Production rejects the development secret and wildcard origins, uses HttpOnly session cookies, and omits demo login controls. For a first production startup without an existing active administrator, provide `ADMIN_BOOTSTRAP_EMAIL` and a unique `ADMIN_BOOTSTRAP_PASSWORD` (12+ characters); the app disables the shared demo accounts and records that action. Remove the bootstrap password from the environment after the admin account is created.

The imported scheme catalog starts unverified. Supabase's previously auto-set verification flags and placeholder dates were cleared; each scheme should be checked against current official sources before an administrator verifies it.

The repository includes a Render Docker deployment configuration. Before treating the public app as a production service, add managed database migrations, distributed login rate limiting, durable private document storage and retention, real OCR dependencies and operational monitoring, and a human review of scheme eligibility and benefits. Render's free service has temporary local storage, so uploaded files do not persist across restarts or deploys.
