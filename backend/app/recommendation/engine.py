from typing import List, Dict, Any, Optional
from app.models.models import Scheme, UserProfile
from app.eligibility.evaluator import EligibilityEvaluator

class RecommendationEngine:
    """
    Transparent Multi-Criteria Government Scheme Recommendation Algorithm.
    Weights:
      - Deterministic Eligibility Match: 40%
      - Location / Jurisdiction Match: 20%
      - Occupation / Profession Match: 15%
      - Income Ceiling Fit: 10%
      - Social Category & Priority: 10%
      - Citizen Need / Search Intent: 5%
    """

    @classmethod
    def score_scheme(
        cls,
        scheme: Scheme,
        profile: Optional[UserProfile],
        user_intent: Optional[str] = None
    ) -> Dict[str, Any]:
        eligibility_report = EligibilityEvaluator.evaluate(scheme, profile)
        
        # 1. Eligibility Score (0 - 100)
        e_status = eligibility_report["status"]
        if e_status == EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE:
            e_score = 98.0
        elif e_status == EligibilityEvaluator.STATUS_MORE_INFO_REQUIRED:
            e_score = 70.0
        elif e_status == EligibilityEvaluator.STATUS_CANNOT_ASSESS:
            e_score = 80.0
        else: # conditions_not_met
            e_score = 20.0

        # If no profile, provide a balanced neutral baseline
        if not profile:
            total_score = int(68 + (scheme.id % 12))
            return {
                "scheme": scheme,
                "match_score": total_score,
                "eligibility_status": EligibilityEvaluator.STATUS_MORE_INFO_REQUIRED,
                "status_label": "Complete Profile for Evaluation",
                "match_reasons": [
                    "Popular national welfare program",
                    f"Category: {scheme.category}",
                    f"Benefit: {scheme.benefit_amount}"
                ],
                "missing_criteria": ["Complete profile to view personal eligibility match"],
                "score_breakdown": {
                    "eligibility": 50,
                    "location": 70,
                    "occupation": 70,
                    "income": 70,
                    "category": 70,
                    "intent": 70
                }
            }

        rule = scheme.eligibility_rules

        # 2. Location match (0 - 100)
        user_state = (profile.state or "").strip().lower()
        loc_score = 75.0
        loc_reason = "Nationwide Central scheme coverage"
        if rule and rule.allowed_states:
            allowed = [s.strip().lower() for s in rule.allowed_states.split(",") if s.strip()]
            if "all" in allowed:
                loc_score = 95.0
                loc_reason = "All-India coverage (Valid across all States & UTs)"
            elif user_state in allowed:
                loc_score = 100.0
                loc_reason = f"Specifically available in {profile.state}"
            elif user_state:
                loc_score = 0.0
                loc_reason = f"Restricted to {rule.allowed_states}"
        elif scheme.applicable_states:
            if "all" in scheme.applicable_states.lower():
                loc_score = 95.0
                loc_reason = "Universal State/UT eligibility"
            elif user_state and user_state in scheme.applicable_states.lower():
                loc_score = 100.0
                loc_reason = f"Applicable in {profile.state}"
            else:
                loc_score = 25.0

        # 3. Occupation match (0 - 100)
        user_occ = (profile.occupation or "").strip().lower()
        occ_score = 70.0
        occ_reason = "Open to citizens across all occupations"
        if rule and rule.allowed_occupations:
            allowed_occs = [o.strip().lower() for o in rule.allowed_occupations.split(",") if o.strip()]
            if "all" in allowed_occs:
                occ_score = 85.0
                occ_reason = "Universal occupation eligibility"
            elif any(allowed in user_occ or user_occ in allowed for allowed in allowed_occs):
                occ_score = 100.0
                occ_reason = f"Targeted directly to your profession ({profile.occupation})"
            elif user_occ:
                occ_score = 20.0
                occ_reason = f"Primarily designated for: {rule.allowed_occupations}"

        # 4. Income match (0 - 100)
        user_income = profile.annual_income
        inc_score = 80.0
        inc_reason = "Standard income qualification"
        if rule and rule.max_annual_income:
            if user_income is not None:
                if user_income <= rule.max_annual_income:
                    inc_score = 100.0
                    inc_reason = f"Income within criteria (₹{user_income:,.0f} <= ₹{rule.max_annual_income:,.0f})"
                else:
                    inc_score = 0.0
                    inc_reason = f"Income exceeds ceiling of ₹{rule.max_annual_income:,.0f}"
            else:
                inc_score = 65.0
                inc_reason = f"Income ceiling: ₹{rule.max_annual_income:,.0f}"

        # 5. Social Category match (0 - 100)
        user_cat = (profile.social_category or "").strip().lower()
        cat_score = 75.0
        if rule and rule.allowed_categories:
            allowed_cats = [c.strip().lower() for c in rule.allowed_categories.split(",") if c.strip()]
            if "all" in allowed_cats:
                cat_score = 85.0
            elif user_cat in allowed_cats:
                cat_score = 100.0
            elif user_cat:
                cat_score = 20.0

        # Priority bonus for special flags
        if profile.has_bpl_card and rule and rule.bpl_required:
            cat_score = 100.0
        if profile.is_disabled and rule and rule.disability_required:
            cat_score = 100.0

        # 6. Intent & Category relevance (0 - 100)
        intent_score = 50.0
        if user_intent:
            intent_lower = user_intent.lower()
            if scheme.category.lower() in intent_lower or scheme.name.lower() in intent_lower or (scheme.short_name and scheme.short_name.lower() in intent_lower):
                intent_score = 100.0
            elif any(w in intent_lower for w in scheme.name.lower().split() if len(w) > 3):
                intent_score = 85.0

        # Weighted calculation
        total_score_float = (
            (e_score * 0.40) +
            (loc_score * 0.20) +
            (occ_score * 0.15) +
            (inc_score * 0.10) +
            (cat_score * 0.10) +
            (intent_score * 0.05)
        )

        final_score = int(round(total_score_float))
        final_score = max(15, min(98, final_score))

        # Collect punchy, explainable match reasons
        reasons: List[str] = []
        if occ_score >= 85 and profile.occupation:
            reasons.append(f"Occupation match: {profile.occupation}")
        if loc_score >= 85 and profile.state:
            reasons.append(f"State eligibility: {profile.state}")
        if inc_score >= 85 and user_income is not None:
            reasons.append("Income criteria satisfied")
        if profile.is_rural and rule and rule.rural_only:
            reasons.append("Rural resident priority")
        if profile.landholding_acres and profile.landholding_acres > 0 and rule and rule.requires_landholding:
            reasons.append(f"Landholding verified ({profile.landholding_acres} acres)")
        if cat_score >= 95 and profile.social_category and profile.social_category != "General":
            reasons.append(f"Category priority: {profile.social_category}")

        if len(reasons) < 2 and eligibility_report.get("satisfied_criteria"):
            for m in eligibility_report["satisfied_criteria"][:2]:
                if m not in reasons:
                    reasons.append(m)

        if not reasons:
            reasons = [scheme.summary[:90] + "..."]

        return {
            "scheme": scheme,
            "match_score": final_score,
            "eligibility_status": eligibility_report["status"],
            "status_label": eligibility_report["status_label"],
            "match_reasons": reasons,
            "missing_criteria": eligibility_report.get("unmet_criteria", []) or eligibility_report.get("unknown_criteria", []),
            "score_breakdown": {
                "eligibility": int(e_score),
                "location": int(loc_score),
                "occupation": int(occ_score),
                "income": int(inc_score),
                "category": int(cat_score),
                "intent": int(intent_score)
            }
        }

    @classmethod
    def rank_schemes(
        cls,
        schemes: List[Scheme],
        profile: Optional[UserProfile],
        user_intent: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        scored = [
            cls.score_scheme(scheme, profile, user_intent)
            for scheme in schemes
            if scheme.is_active
        ]
        # Rank: Likely Eligible first, then More Info Required, then Not Eligible
        status_priority = {
            EligibilityEvaluator.STATUS_LIKELY_ELIGIBLE: 3,
            EligibilityEvaluator.STATUS_MORE_INFO_REQUIRED: 2,
            EligibilityEvaluator.STATUS_CANNOT_ASSESS: 2,
            EligibilityEvaluator.STATUS_CONDITIONS_NOT_MET: 1
        }
        scored.sort(
            key=lambda x: (
                status_priority.get(x["eligibility_status"], 0),
                x["match_score"]
            ),
            reverse=True
        )
        return scored[:limit]
