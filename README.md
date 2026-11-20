# JanSahay | AI-Based Government Scheme Recommendation System

> **Tagline:** *"Government benefits, matched to you."*  
> **Target Audience:** Indian Citizens (Farmers, Students, Women, Small Business Owners, Senior Citizens, Artisans)  
> **Stack:** React 18, Vite, Tailwind CSS, Lucide Icons, FastAPI (Python 3.10+), SQLAlchemy, SQLite / PostgreSQL ready.

---

## 1. Project Overview

**JanSahay** is an AI-powered civic technology platform designed to bridge the awareness and accessibility gap between Indian citizens and government welfare schemes. Instead of navigating dozens of confusing ministry websites, a citizen enters their basic demographic profile (age, state, occupation, income, category, landholding) and instantly receives:

1. **Rule-Based Eligibility Evaluation:** Transparent audit of which criteria passed or failed.
2. **Ranked Personalized Recommendations:** Multi-criteria weighted compatibility scoring.
3. **Conversational Scheme Assistant:** An AI chatbot with voice interaction that understands natural queries (e.g., *"I am a farmer in Maharashtra. What schemes can I get?"*) and explains *"Why am I eligible?"*.
4. **Actionable Application Roadmaps:** Benefit amounts, mandatory document checklists (Aadhaar, 7/12 Land extract, Income certificates), and direct links to official government portals.
5. **Multilingual Interface:** English, Hindi (हिन्दी), and Marathi (मराठी).

---

## 2. Core Features

### 🏛️ Civic-Tech Design & Mature UX
- Designed with public-service dignity: Deep Teal (`#0F766E`), Trustworthy Blue (`#2563EB`), neutral slate surfaces (`#F8FAFC`), 1px borders, Inter typography, and no AI-generated gradients or decorative gimmicks.
- Verified portal badges and official legal disclaimers.

### ⚙️ Rule-Based Eligibility Engine
- Evaluates strict mathematical constraints:
  - Age brackets (`min_age` ≤ `user.age` ≤ `max_age`)
  - State jurisdiction (`allowed_states`)
  - Occupation matching (`allowed_occupations`)
  - Annual income ceilings (`max_annual_income`)
  - Landholding thresholds for agricultural schemes (`landholding_acres` ≤ `max_landholding`)
  - Rural vs. Urban residency (`is_rural`)
  - Special conditions (BPL card, PwD / Divyangjan status, Student status, Minorities)
- Returns categorized results: `likely_eligible`, `possibly_eligible`, and `not_eligible` with full transparency.

### 📊 Transparent Recommendation Algorithm
Scoring breakdown:
$$\text{Score} = (E \times 0.40) + (L \times 0.20) + (O \times 0.15) + (I \times 0.10) + (C \times 0.10) + (U \times 0.05)$$
- **Eligibility Match ($E$):** 40%
- **Location Match ($L$):** 20%
- **Occupation Relevance ($O$):** 15%
- **Income Relevance ($I$):** 10%
- **Category Match ($C$):** 10%
- **User Intent / Context ($U$):** 5%

### 🤖 Conversational AI Scheme Assistant
- Natural language query understanding for agriculture, education, healthcare, housing, business, and social security.
- **Embedded Scheme Cards:** Renders rich cards inline in the conversation.
- **Explainability:** Answers *"Why am I eligible for this scheme?"* with a bulleted audit.
- **Voice UI:** Web Speech API integration with microphone animation and fallback to standard text input.

### 🇮🇳 Multilingual Support (i18n)
- Dynamic instant switching between English, Hindi (हिन्दी), and Marathi (मराठी).

### 🛡️ Administrative Portal
- Verification desk to audit schemes, monitor catalog statistics, toggle verified badges, and add new schemes.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6, Lucide React |
| **Backend API** | FastAPI (Python 3.10+), Pydantic v2, Uvicorn |
| **Database** | SQLAlchemy 2.0 ORM, SQLite (`jansahay.db` default), PostgreSQL ready |
| **Authentication** | PBKDF2-HMAC-SHA256 password hashing, HMAC-SHA256 JWT tokens |
| **Voice / Audio** | Web Speech API (`webkitSpeechRecognition` / `SpeechRecognition`) |

---

## 4. Project Directory Structure

```
government-scheme-ai/
│
├── frontend/                        # React + Vite + Tailwind frontend
│   ├── src/
│   │   ├── components/              # SchemeCard, EligibilityBadge, Navbar, Sidebar, Footer, VoiceInputModal
│   │   ├── pages/                   # Landing, Login, Onboarding, Dashboard, Schemes, Details, Chat, Profile, Admin
│   │   ├── layouts/                 # PublicLayout, AppLayout
│   │   ├── context/                 # AuthContext, LanguageContext
│   │   ├── services/                # api.js, speech.js
│   │   ├── i18n/                    # translations.js (English, Hindi, Marathi)
│   │   ├── App.jsx                  # Main application router
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md
│
├── backend/                         # FastAPI backend
│   ├── app/
│   │   ├── api/                     # auth, schemes, recommendations, eligibility, chat, admin
│   │   ├── models/                  # SQLAlchemy User, Profile, Scheme, EligibilityRule, Benefits, Documents
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── eligibility/             # Rule-based eligibility evaluator
│   │   ├── recommendation/          # Transparent multi-criteria scoring engine
│   │   ├── services/                # Auth tokens, Chat intent classifier & explainability
│   │   ├── database/                # Session manager & seed script
│   │   ├── config.py
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── requirements.txt
│   └── README.md
│
├── data/
│   └── indian_government_schemes_dataset_english_and_hindi.csv
│
├── demo/
├── Dockerfile                      # Single-container frontend + API for Render
├── render.yaml                     # Render Blueprint
├── .env.example
└── README.md
```

---

## 5. Quick Start (Running Locally)

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.10+)

---

### Step 1: Run the Backend API

```bash
# Navigate to backend directory
cd backend

# Install Python requirements
pip install -r requirements.txt

# Run development server (Auto-seeds database on first run)
uvicorn app.main:app --reload --port 8000
```

The backend starts at `http://127.0.0.1:8000`.  
The working Link at 'https://jansahay-0eh4.onrender.com/'.
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`.

---

### Step 2: Run the Frontend UI

Open a second terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite dev server
npm run dev
```

The frontend will run at `http://localhost:5173`. Open this URL in your browser.

---

## 6. Local Development Demo Accounts

| Persona | Email | Password | Details |
|---|---|---|---|
| **Citizen (Rameshwar Patil)** | `demo@citizen.in` | `Citizen@2026` | Farmer, Nashik, Maharashtra, age 38, INR 180,000 income, 2.5 acres. |
| **Portal Administrator** | `admin@jansahay.gov.in` | `Admin@JanSahay2026` | Local development account only. |

These shared demo accounts are created only in development when `ENABLE_DEMO_ACCOUNTS=true`. Never enable them in production. The one-click login panel is omitted from production builds.

---

## 7. Sample Schemes in Seed Database

The database comes pre-seeded with 20 realistic Indian government schemes:
1. **PM-KISAN** (Pradhan Mantri Kisan Samman Nidhi) — Agriculture
2. **Namo Shetkari Maha Samman Nidhi** — Maharashtra State Agriculture
3. **PMFBY** (Pradhan Mantri Fasal Bima Yojana) — Crop Insurance
4. **Ayushman Bharat PM-JAY** — Healthcare Cover (₹5 Lakh)
5. **PMAY-G** (Pradhan Mantri Awaas Yojana - Gramin) — Rural Housing
6. **PM SVANidhi** — Street Vendor Micro-Credit
7. **PMMY** (Pradhan Mantri Mudra Yojana) — Micro-Business Loans
8. **PM-USP Central Sector Scholarship** — Higher Education
9. **PMS-SC/ST** (Post-Matric Scholarship) — Education Reimbursement
10. **RCSM EBC Scholarship** — Maharashtra Higher Education Fee Relief
11. **Sukanya Samriddhi Yojana** — Girl Child Savings (8.2%)
12. **Atal Pension Yojana (APY)** — Unorganized Sector Pension
13. **PM Vishwakarma Scheme** — Traditional Artisans & Craftspersons
14. **Stand-Up India Scheme** — Greenfield Enterprise Financing
15. **PMEGP** — Credit-Linked Employment Generation
16. **Janani Suraksha Yojana** — Safe Motherhood Cash Assistance
17. **PM-KMY** (Kisan Maan Dhan Yojana) — Small Farmer Old-Age Pension
18. **Divyangjan Swavalamban Yojana** — Concessional Disability Credit
19. **Senior Citizen Savings Scheme (SCSS)** — 8.2% Retirement Safety
20. **Pradhan Mantri Ujjwala Yojana 2.0** — Clean Cooking LPG Assistance

---

## 8. Presentation Flow (3 Minutes)

1. **Landing Page (`/`):** Demonstrate the civic-tech aesthetic, official Government of India bar, and three-step architecture diagram.
2. **Onboarding (`/onboarding`):** Show the 6-step progress wizard. Click *"Quick Demo Fill (Rahul Sharma)"* and submit.
3. **Dashboard (`/dashboard`):** Show the personalized recommendations. Highlight that **PM-KISAN** and **Namo Shetkari Yojana** appear at the top with **94%–97% Match Scores** with clear reason bullets.
4. **Scheme Details (`/schemes/:id`):** Open PM-KISAN, show the *"Why you were recommended"* box, document checklist, and official disclaimer.
5. **AI Assistant (`/chat`):** Ask *"I am a farmer in Maharashtra. What schemes can I get?"* and show embedded scheme cards. Then ask *"Why am I eligible for this scheme?"* to reveal the rule engine audit. Show the voice mic button.
6. **Localization:** Switch language in the navbar to **हिन्दी** or **मराठी** to demonstrate instant multilingual rendering.

---

## 9. Security & Architecture Notes

- Passwords hashed using PBKDF2-HMAC-SHA256 with cryptographic salt.
- JWT tokens signed using HMAC-SHA256.
- Database normalized with SQLAlchemy relationships across schemes, eligibility rules, benefits, documents, and application tracks.
- Ready for Render deployment using the root `Dockerfile` and `render.yaml`.

## Deploy on Render

The Render Blueprint creates one Docker web service that serves the Vite frontend and FastAPI API from the same origin. This keeps the production login cookie and `/api` requests on the same host. The blueprint uses the Singapore region and Render's free web-service plan; free services can sleep when idle and their local files are temporary.

1. Push this repository to a private GitHub repository and connect it to Render.
2. In Render, choose **New → Blueprint** and select the repository. Review `render.yaml` before applying it.
3. Enter the Supabase PostgreSQL connection URL as `DATABASE_URL`. Use the SQLAlchemy `postgresql+psycopg://` form, URL-encode the password, and require SSL.
4. Enter the administrator email and a unique password of at least 12 characters. Add `GROQ_API_KEY` only if you want the hosted chat to use Groq.
5. After Render assigns the service URL, make sure `CORS_ALLOWED_ORIGINS` is exactly that `https://…onrender.com` origin, then redeploy.
6. Wait for `/api/health` to report a healthy database connection and open the service URL.

Keep secrets in Render's environment settings, never in Git. The Supabase database should already contain the scheme catalog and user records before the first launch. The free Render filesystem is temporary: uploaded document files are not durable there. Do not use document uploads for real personal records until persistent or object storage and a retention policy are configured. Free services can sleep after inactivity, and the first request may take about a minute to wake them.

---

## 10. License & Academic Disclaimer

Developed for academic demonstration and presentation purposes. All scheme guidelines, documents, and benefits are referenced from verified official Indian Government portals (india.gov.in, pmkisan.gov.in, pmjay.gov.in).
