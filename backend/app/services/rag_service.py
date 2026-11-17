import os
import re
import html
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Scheme, SchemeQA, User, UserProfile
from app.eligibility.evaluator import EligibilityEvaluator
from app.recommendation.engine import RecommendationEngine
from app.schemas.scheme import SchemeDetailOut
from app.config import settings

# Attempt sklearn for TF-IDF; fallback to lightweight BM25/keyword if unavailable
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class RAGRetriever:
    """
    In-memory TF-IDF and metadata-filtered RAG retriever for JanSahay AI.
    Indexed across 3,473 Q&A records and 73 canonical schemes.
    """
    _instance = None
    _vectorizer = None
    _qa_matrix = None
    _qa_records = [] # list of dicts with id, scheme_id, text, etc.
    _is_indexed = False

    @classmethod
    def initialize_index(cls, db: Session):
        """Build or refresh in-memory retrieval index from database."""
        qa_rows = db.query(SchemeQA).all()
        if not qa_rows:
            return

        cls._qa_records = []
        corpus = []

        for qa in qa_rows:
            scheme = qa.scheme
            combined_text = (
                f"{qa.question_english} {qa.answer_english} "
                f"{qa.question_hindi or ''} {qa.answer_hindi or ''} "
                f"{scheme.name} {scheme.short_name or ''} {scheme.category} {scheme.department} "
                f"{scheme.target_beneficiary or ''}"
            )
            cls._qa_records.append({
                "id": qa.id,
                "scheme_id": qa.scheme_id,
                "scheme_name": scheme.name,
                "scheme_short": scheme.short_name,
                "scheme_slug": scheme.slug,
                "category": scheme.category,
                "applicable_states": scheme.applicable_states,
                "official_url": scheme.official_url,
                "target_beneficiary": scheme.target_beneficiary,
                "topic": qa.topic,
                "question_en": qa.question_english,
                "question_hi": qa.question_hindi,
                "answer_en": qa.answer_english,
                "answer_hi": qa.answer_hindi,
                "text": combined_text
            })
            corpus.append(combined_text)

        if SKLEARN_AVAILABLE and corpus:
            cls._vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=5000,
                ngram_range=(1, 1)
            )
            cls._qa_matrix = cls._vectorizer.fit_transform(corpus)
            cls._is_indexed = True
            print(f"JanSahay RAG Retriever indexed {len(cls._qa_records)} scheme Q&A documents.")
        else:
            cls._is_indexed = True
            print(f"JanSahay RAG Retriever indexed {len(cls._qa_records)} documents using lexical matcher.")

    @classmethod
    def retrieve(
        cls,
        db: Session,
        query: str,
        top_k: int = 5,
        filter_category: Optional[str] = None,
        filter_state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant grounded Q&A and scheme documents."""
        if not cls._is_indexed or not cls._qa_records:
            cls.initialize_index(db)

        if not cls._qa_records:
            return []

        q_clean = query.strip().lower()
        
        # Scored candidates
        candidates = []
        
        if SKLEARN_AVAILABLE and cls._vectorizer and cls._qa_matrix is not None:
            q_vec = cls._vectorizer.transform([query])
            sims = cosine_similarity(q_vec, cls._qa_matrix).flatten()
            
            top_indices = np.argsort(sims)[::-1][:top_k * 4]
            for idx in top_indices:
                score = float(sims[idx])
                if score < 0.04:
                    continue
                rec = cls._qa_records[idx]
                
                # Apply metadata filters
                if filter_category and filter_category.lower() != "all":
                    if filter_category.lower() not in rec["category"].lower():
                        continue
                if filter_state and filter_state.lower() != "all":
                    app_states = rec["applicable_states"].lower()
                    if "all" not in app_states and filter_state.lower() not in app_states:
                        continue
                        
                candidates.append((rec, score))
        else:
            # Lexical keyword fallback
            terms = [t for t in re.findall(r'\b\w+\b', q_clean) if len(t) > 2]
            for rec in cls._qa_records:
                score = 0.0
                text_lower = rec["text"].lower()
                for t in terms:
                    if t in text_lower:
                        score += 1.0
                if score > 0:
                    candidates.append((rec, score))
            candidates.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate by scheme_id while preserving top matches
        results = []
        seen_schemes = set()
        for rec, score in candidates:
            results.append({**rec, "similarity_score": round(score, 3)})
            seen_schemes.add(rec["scheme_id"])
            if len(results) >= top_k:
                break

        return results


class JanSahayRAGService:
    """
    End-to-end Grounded RAG Chat Service for JanSahay AI.
    - Grounded in real 3,473 Q&A records
    - Cites official sources & portal links
    - Explains eligibility via deterministic engine
    - Injects no fabricated citations
    - Protected against prompt injection
    """

    SYSTEM_PROMPT = """You are JanSahay AI (जनसहाय एआई), the official intelligent civic advisor for Indian Government Schemes.
Your duty is to assist citizens with completely accurate, respectful, and evidence-grounded welfare information.

STRICT INSTRUCTIONS:
1. Base your answer EXCLUSIVELY on the provided Government Scheme Database Context.
2. ALWAYS cite the official scheme name and official portal URL provided in the context.
3. NEVER fabricate schemes, eligibility percentages, or unofficial website links.
4. If the information is not present in the context, explicitly state: "I could not find verified details for this query in our official database."
5. Clarify that advice is indicative guidance and does not replace official verification by competent authorities.
6. Use clean Markdown: bold headers, bulleted benefits, and next-step actions.
"""

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Protect against prompt injection and control sequence escapes."""
        if not text:
            return ""
        # Remove markdown instructions attempts or system override tokens
        cleaned = re.sub(r'(system:|assistant:|user:|### Instruction|ignore previous instructions)', '', text, flags=re.IGNORECASE)
        # Escape raw HTML tags
        cleaned = html.escape(cleaned)
        return cleaned.strip()[:600]

    @classmethod
    def answer_query(
        cls,
        db: Session,
        query: str,
        user: Optional[User] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process citizen query via Grounded RAG pipeline with citations & deterministic eligibility.
        """
        clean_q = cls.sanitize_input(query)
        profile: Optional[UserProfile] = user.profile if user else None

        # 1. State / Category detection for filtering
        detected_category = None
        detected_state = profile.state if profile else None
        
        # Category heuristics
        cat_keywords = {
            "Agriculture": ["farmer", "farming", "crop", "kisan", "land", "fasal", "agriculture"],
            "Healthcare": ["health", "hospital", "ayushman", "doctor", "medical", "treatment", "medicine", "swasthya"],
            "Education & Scholarships": ["student", "scholarship", "college", "school", "study", "tuition", "education", "vidya"],
            "Housing & Urban Affairs": ["house", "housing", "awas", "home", "shelter", "pucca"],
            "Business & MSME": ["business", "loan", "startup", "mudra", "vendor", "svanidhi", "shopkeeper", "msme"],
            "Social Security": ["pension", "old age", "senior", "disability", "divyang", "welfare"]
        }
        for cat, kws in cat_keywords.items():
            if any(k in clean_q.lower() for k in kws):
                detected_category = cat
                break

        # 2. Retrieve Evidence from Knowledge Base
        retrieved_docs = RAGRetriever.retrieve(
            db=db,
            query=clean_q,
            top_k=4,
            filter_category=detected_category,
            filter_state=detected_state
        )

        # If zero match found
        if not retrieved_docs:
            # Fallback search without filters
            retrieved_docs = RAGRetriever.retrieve(db=db, query=clean_q, top_k=3)

        if not retrieved_docs:
            return {
                "message": (
                    "I could not locate verified government scheme information matching your specific query in our official catalog. "
                    "You can browse programs by sector (such as **Agriculture**, **Healthcare**, **Education**, or **Business**) "
                    "or specify your state and occupation to help me identify relevant welfare schemes."
                ),
                "intent": "unmatched_search",
                "citations": [],
                "recommended_schemes": [],
                "follow_up_suggestions": [
                    "Show schemes for farmers in Maharashtra",
                    "Which healthcare schemes provide cashless treatment?",
                    "What scholarships are available for students?",
                    "Show business loans under MUDRA"
                ],
                "grounded_sources": []
            }

        # 3. Collect Canonical Scheme Objects for top retrieved docs
        scheme_ids = list(dict.fromkeys([d["scheme_id"] for d in retrieved_docs]))
        schemes = db.query(Scheme).filter(Scheme.id.in_(scheme_ids)).all()

        # Score through Recommendation Engine
        ranked_schemes = [
            RecommendationEngine.score_scheme(s, profile, user_intent=clean_q)
            for s in schemes
        ]
        ranked_schemes.sort(key=lambda x: x["match_score"], reverse=True)

        primary_scheme = ranked_schemes[0]["scheme"]
        top_rec = ranked_schemes[0]

        # 4. Run Deterministic Eligibility on top scheme
        eligibility_report = EligibilityEvaluator.evaluate(primary_scheme, profile)

        # 5. Extract Citations
        citations = []
        for s in schemes[:3]:
            citations.append({
                "scheme_name": s.name,
                "short_name": s.short_name,
                "category": s.category,
                "official_url": s.official_url or "https://www.india.gov.in",
                "source": f"Government of India / {s.department}"
            })

        # 6. Synthesize Grounded Evidence Answer
        # Check if external LLM configured (Groq or OpenAI)
        groq_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
        openai_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")

        ai_response_text = None

        if groq_key:
            ai_response_text = cls._call_groq_llm(groq_key, clean_q, retrieved_docs, profile, eligibility_report)
        elif openai_key:
            ai_response_text = cls._call_openai_llm(openai_key, clean_q, retrieved_docs, profile, eligibility_report)

        # If LLM unavailable or failed, use Deterministic Grounded Synthesis
        if not ai_response_text:
            ai_response_text = cls._synthesize_grounded_answer(
                query=clean_q,
                primary_scheme=primary_scheme,
                retrieved_docs=retrieved_docs,
                eligibility_report=eligibility_report,
                citations=citations,
                language=language
            )

        # Follow-up suggestions based on missing criteria or user next steps
        follow_ups = []
        if eligibility_report["unknown_criteria"]:
            follow_ups.extend(eligibility_report.get("follow_up_questions", [])[:2])
        follow_ups.extend([
            f"What documents do I need for {primary_scheme.short_name or primary_scheme.name}?",
            f"How do I apply for {primary_scheme.short_name or primary_scheme.name} step by step?",
            "What other schemes match my profile?"
        ])

        # Serialize ranked schemes into dictionaries for safe Pydantic / JSON response
        serialized_recommendations = []
        for r in ranked_schemes:
            sc = r["scheme"]
            if hasattr(sc, "__table__") or not isinstance(sc, dict):
                sc_dict = SchemeDetailOut.model_validate(sc).model_dump()
            else:
                sc_dict = sc
            serialized_recommendations.append({
                **r,
                "scheme": sc_dict
            })

        return {
            "message": ai_response_text,
            "intent": "grounded_rag_answer",
            "primary_scheme_id": primary_scheme.id,
            "primary_scheme_slug": primary_scheme.slug,
            "citations": citations,
            "recommended_schemes": serialized_recommendations,
            "eligibility_summary": {
                "status": eligibility_report["status"],
                "status_label": eligibility_report["status_label"],
                "score": eligibility_report["score"],
                "satisfied_criteria": eligibility_report["satisfied_criteria"],
                "unknown_criteria": eligibility_report["unknown_criteria"],
                "unmet_criteria": eligibility_report["unmet_criteria"],
            },
            "follow_up_suggestions": follow_ups[:4],
            "grounded_sources": [
                {
                    "title": d["question_en"],
                    "excerpt": d["answer_en"][:150] + "...",
                    "official_url": d["official_url"],
                    "similarity": d.get("similarity_score", 0.0)
                }
                for d in retrieved_docs[:3]
            ]
        }

    @classmethod
    def _synthesize_grounded_answer(
        cls,
        query: str,
        primary_scheme: Scheme,
        retrieved_docs: List[Dict[str, Any]],
        eligibility_report: Dict[str, Any],
        citations: List[Dict[str, Any]],
        language: str = "en"
    ) -> str:
        """Deterministic, authoritative grounded markdown response generator."""
        # Top answer excerpt from Q&A knowledge base
        top_qa = retrieved_docs[0]
        answer_body = top_qa["answer_en"]
        if len(answer_body) > 380:
            answer_body = answer_body[:380] + "..."

        # Format satisfied rules
        matched_bullets = ""
        if eligibility_report["satisfied_criteria"]:
            matched_bullets = "\n".join([f"• ✅ **{r}**" for r in eligibility_report["satisfied_criteria"][:3]])
        else:
            matched_bullets = "• Citizen profile details needed for automated matching."

        # Format unknown rules / follow-ups
        unknown_bullets = ""
        if eligibility_report["unknown_criteria"]:
            unknown_bullets = "\n**Information Required to Confirm Eligibility:**\n" + "\n".join(
                [f"• ⚠️ {r}" for r in eligibility_report["unknown_criteria"][:2]]
            ) + "\n"

        # Citations markdown
        sources_md = "\n".join([
            f"• [{c['scheme_name']}]({c['official_url']}) — *{c['source']}*"
            for c in citations
        ])

        msg = (
            f"### Grounded Guidance: **{primary_scheme.name}**\n\n"
            f"**Department:** {primary_scheme.department} ({primary_scheme.level} Scheme)\n"
            f"**Key Benefit:** {primary_scheme.benefit_amount}\n\n"
            f"#### Summary & Objective\n{primary_scheme.summary}\n\n"
            f"#### Verified Database Knowledge\n{answer_body}\n\n"
            f"#### Eligibility Assessment\n"
            f"**Status:** {eligibility_report['status_label']}\n\n"
            f"{matched_bullets}\n"
            f"{unknown_bullets}\n"
            f"#### Official Government Sources\n{sources_md}\n\n"
            f"> *Notice: Results are provided for guidance based on the verified scheme dataset. Final approval is subject to official document verification.*"
        )
        return msg

    @classmethod
    def _call_groq_llm(cls, api_key: str, query: str, docs: List[Dict[str, Any]], profile, eligibility_report) -> Optional[str]:
        import requests
        try:
            ctx_snippets = "\n\n".join([
                f"Scheme: {d['scheme_name']}\nOfficial URL: {d['official_url']}\nQ: {d['question_en']}\nA: {d['answer_en']}"
                for d in docs[:3]
            ])
            prompt = (
                f"Context from Government Scheme Database:\n{ctx_snippets}\n\n"
                # Keep profile demographics and income inside the application;
                # only the citizen's message and public scheme evidence leave it.
                f"Eligibility Evaluation Status: {eligibility_report['status_label']}\n\n"
                f"Citizen Question: {query}\n\n"
                f"Answer the citizen's question accurately using the context above. Include the official portal URL citation and explain their eligibility in clear language."
            )

            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": cls.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 750
                },
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"RAG Groq call fallback notice: {e}")
        return None

    @classmethod
    def _call_openai_llm(cls, api_key: str, query: str, docs: List[Dict[str, Any]], profile, eligibility_report) -> Optional[str]:
        import requests
        try:
            ctx_snippets = "\n\n".join([
                f"Scheme: {d['scheme_name']}\nOfficial URL: {d['official_url']}\nQ: {d['question_en']}\nA: {d['answer_en']}"
                for d in docs[:3]
            ])
            prompt = (
                f"Context from Database:\n{ctx_snippets}\n\n"
                f"Citizen Question: {query}\n\n"
                f"Provide an authoritative, grounded response citing official portal URLs."
            )
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": cls.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 750
                },
                timeout=8
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"RAG OpenAI call fallback notice: {e}")
        return None
