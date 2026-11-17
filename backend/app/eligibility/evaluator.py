from typing import Dict, Any, List, Optional
from app.models.models import Scheme, EligibilityRule, UserProfile

DISCLAIMER_TEXT = (
    "JanSahay AI Guidance Notice: Eligibility evaluations are indicative recommendations based on "
    "available data and citizen-provided profile details. Official sanctions and approvals are "
    "governed solely by the respective Government Department / Ministry upon formal document verification."
)

class EligibilityEvaluator:
    """
    Deterministic, explainable, and transparent Civic Eligibility Engine for Indian Government Schemes.
    Strictly distinguishes satisfied, unmet, and unknown criteria without assuming or fabricating rules.
    """

    STATUS_LIKELY_ELIGIBLE = "likely_eligible"
    STATUS_MORE_INFO_REQUIRED = "more_info_required"
    STATUS_CONDITIONS_NOT_MET = "conditions_not_met"
    STATUS_CANNOT_ASSESS = "cannot_assess"

    LABEL_MAP = {
        STATUS_LIKELY_ELIGIBLE: "Likely eligible based on available information",
        STATUS_MORE_INFO_REQUIRED: "More information required to confirm eligibility",
        STATUS_CONDITIONS_NOT_MET: "One or more eligibility conditions not met",
        STATUS_CANNOT_ASSESS: "Eligibility cannot be assessed from the available data"
    }

    @classmethod
    def evaluate(cls, scheme: Scheme, profile: Optional[UserProfile or Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate a user profile against a scheme's eligibility rules with full transparency.
        """
        # If no profile provided at all
        if not profile:
            required_docs = [
                {"name": d.document_name, "mandatory": d.is_mandatory, "notes": d.notes}
                for d in getattr(scheme, "documents", [])
            ] if getattr(scheme, "documents", None) else []

            return {
                "scheme_id": getattr(scheme, "id", None),
                "scheme_name": getattr(scheme, "name", "General Scheme"),
                "status": cls.STATUS_MORE_INFO_REQUIRED,
                "status_label": cls.LABEL_MAP[cls.STATUS_MORE_INFO_REQUIRED],
                "score": 50,
                "satisfied_criteria": [],
                "unmet_criteria": [],
                "unknown_criteria": [
                    "Citizen profile details (Age, State, Occupation, Income) have not been provided."
                ],
                "follow_up_questions": [
                    "What is your age and residential state?",
                    "What is your current occupation and approximate annual income?"
                ],
                "required_documents": required_docs,
                "matched_rules": ["Central / State welfare program"],
                "failed_rules": [],
                "neutral_rules": ["Please complete your profile to obtain a verified eligibility audit."],
                "summary_reason": "Profile information is required to evaluate eligibility against official guidelines.",
                "action_tip": "Complete your citizen profile or answer the follow-up questions to verify eligibility.",
                "disclaimer": DISCLAIMER_TEXT
            }

        # Normalize profile into dict
        p: Dict[str, Any] = {}
        if hasattr(profile, "__dict__"):
            p = {
                "age": getattr(profile, "age", None),
                "gender": getattr(profile, "gender", None),
                "state": getattr(profile, "state", None),
                "district": getattr(profile, "district", None),
                "occupation": getattr(profile, "occupation", None),
                "annual_income": getattr(profile, "annual_income", None),
                "social_category": getattr(profile, "social_category", None),
                "is_rural": getattr(profile, "is_rural", None),
                "landholding_acres": getattr(profile, "landholding_acres", 0.0),
                "is_disabled": getattr(profile, "is_disabled", False),
                "has_bpl_card": getattr(profile, "has_bpl_card", False),
                "is_student": getattr(profile, "is_student", False),
                "education_level": getattr(profile, "education_level", None),
                "minority": getattr(profile, "minority", False),
            }
        else:
            p = profile

        rule: Optional[EligibilityRule] = getattr(scheme, "eligibility_rules", None)
        
        # If no specific eligibility rules are defined
        if not rule:
            required_docs = [
                {"name": d.document_name, "mandatory": d.is_mandatory, "notes": d.notes}
                for d in scheme.documents
            ] if scheme.documents else []

            return {
                "scheme_id": scheme.id,
                "scheme_name": scheme.name,
                "status": cls.STATUS_CANNOT_ASSESS,
                "status_label": cls.LABEL_MAP[cls.STATUS_CANNOT_ASSESS],
                "score": 75,
                "satisfied_criteria": ["Open public welfare initiative with broad inclusion guidelines"],
                "unmet_criteria": [],
                "unknown_criteria": [],
                "follow_up_questions": [],
                "required_documents": required_docs,
                "matched_rules": ["Broad inclusion scheme"],
                "failed_rules": [],
                "neutral_rules": ["No restrictive exclusion parameters published in central catalog"],
                "summary_reason": "Scheme operates with broad inclusion criteria. Check required documentation before applying.",
                "action_tip": "Review the official guidelines and ensure you have the listed documents.",
                "disclaimer": DISCLAIMER_TEXT
            }

        satisfied_criteria: List[str] = []
        unmet_criteria: List[str] = []
        unknown_criteria: List[str] = []
        follow_up_questions: List[str] = []

        total_rules_checked = 0
        passed_rules_count = 0

        # 1. State & Location Check
        allowed_states_raw = (rule.allowed_states or "All").strip()
        allowed_states = [s.strip().lower() for s in allowed_states_raw.split(",") if s.strip()]
        user_state = (p.get("state") or "").strip().lower()

        if "all" not in allowed_states and allowed_states:
            total_rules_checked += 1
            if not user_state:
                unknown_criteria.append(f"State residency required: {rule.allowed_states}")
                follow_up_questions.append(f"Are you a permanent resident of {rule.allowed_states}?")
            elif user_state in allowed_states:
                passed_rules_count += 1
                satisfied_criteria.append(f"Residency satisfied: Resident of {p.get('state')}")
            else:
                unmet_criteria.append(f"Restricted to residents of {rule.allowed_states} (Your state: {p.get('state')})")
        else:
            satisfied_criteria.append("Pan-India Central Scheme: Open across all Indian States & Union Territories")

        # 2. Age Requirement Check
        user_age = p.get("age")
        has_age_rule = rule.min_age is not None or rule.max_age is not None
        if has_age_rule:
            total_rules_checked += 1
            min_a = rule.min_age or 0
            max_a = rule.max_age or 120
            age_desc = f"{rule.min_age or 'any'} to {rule.max_age or 'any'} years"
            
            if user_age is None:
                unknown_criteria.append(f"Age criterion: Must be between {age_desc} (Not provided in profile)")
                follow_up_questions.append(f"Is your age between {age_desc}?")
            elif (rule.min_age is None or user_age >= rule.min_age) and (rule.max_age is None or user_age <= rule.max_age):
                passed_rules_count += 1
                satisfied_criteria.append(f"Age criteria met: {user_age} years (Allowed bracket: {age_desc})")
            else:
                unmet_criteria.append(f"Age criteria not met: {user_age} years is outside required bracket ({age_desc})")

        # 3. Gender Requirement Check
        allowed_genders_raw = (rule.allowed_genders or "All").strip()
        allowed_genders = [g.strip().lower() for g in allowed_genders_raw.split(",") if g.strip()]
        user_gender = (p.get("gender") or "").strip().lower()

        if "all" not in allowed_genders and allowed_genders:
            total_rules_checked += 1
            if not user_gender:
                unknown_criteria.append(f"Target beneficiary gender: {rule.allowed_genders}")
                follow_up_questions.append(f"Is this application for a {rule.allowed_genders.lower()} beneficiary?")
            elif user_gender in allowed_genders:
                passed_rules_count += 1
                satisfied_criteria.append(f"Gender criteria satisfied: {p.get('gender')}")
            else:
                unmet_criteria.append(f"Scheme is designated exclusively for {rule.allowed_genders} beneficiaries")

        # 4. Occupation & Employment Check
        allowed_occupations_raw = (rule.allowed_occupations or "All").strip()
        allowed_occupations = [o.strip().lower() for o in allowed_occupations_raw.split(",") if o.strip()]
        user_occ = (p.get("occupation") or "").strip().lower()

        if "all" not in allowed_occupations and allowed_occupations:
            total_rules_checked += 1
            if not user_occ:
                unknown_criteria.append(f"Target occupation: {rule.allowed_occupations}")
                follow_up_questions.append(f"Does your profession align with: {rule.allowed_occupations}?")
            else:
                matched_occ = any(allowed in user_occ or user_occ in allowed for allowed in allowed_occupations)
                if matched_occ:
                    passed_rules_count += 1
                    satisfied_criteria.append(f"Occupation requirement satisfied: {p.get('occupation')}")
                else:
                    unmet_criteria.append(f"Target occupation: {rule.allowed_occupations} (Your profile: {p.get('occupation')})")
        else:
            if user_occ:
                satisfied_criteria.append(f"Occupation eligible: Open to all vocational backgrounds")

        # 5. Income Ceiling Check
        user_income = p.get("annual_income")
        if rule.max_annual_income is not None:
            total_rules_checked += 1
            if user_income is None:
                unknown_criteria.append(f"Annual income ceiling: ₹{rule.max_annual_income:,.0f}/year (Not stated in profile)")
                follow_up_questions.append(f"Is your total annual household income below ₹{rule.max_annual_income:,.0f}?")
            elif user_income <= rule.max_annual_income:
                passed_rules_count += 1
                satisfied_criteria.append(f"Income criteria met: ₹{user_income:,.0f} is within ceiling of ₹{rule.max_annual_income:,.0f}/yr")
            else:
                unmet_criteria.append(f"Income exceeds ceiling: ₹{user_income:,.0f} exceeds max allowable ₹{rule.max_annual_income:,.0f}/yr")

        # 6. Social Category Check (SC, ST, OBC, EWS, General)
        allowed_cats_raw = (rule.allowed_categories or "All").strip()
        allowed_cats = [c.strip().lower() for c in allowed_cats_raw.split(",") if c.strip()]
        user_cat = (p.get("social_category") or "").strip().lower()

        if "all" not in allowed_cats and allowed_cats:
            total_rules_checked += 1
            if not user_cat:
                unknown_criteria.append(f"Eligible social categories: {rule.allowed_categories}")
                follow_up_questions.append(f"Do you belong to any of these social categories: {rule.allowed_categories}?")
            elif user_cat in allowed_cats or (user_gender == "female" and "women" in allowed_cats):
                passed_rules_count += 1
                satisfied_criteria.append(f"Social category eligible: {p.get('social_category')}")
            else:
                unmet_criteria.append(f"Exclusively targeted for categories: {rule.allowed_categories}")

        # 7. Rural / Urban Classification Check
        if rule.rural_only is not None:
            total_rules_checked += 1
            user_rural = p.get("is_rural")
            if user_rural is None:
                target_loc = "Rural" if rule.rural_only else "Urban"
                unknown_criteria.append(f"Area classification: Exclusively for {target_loc} residents")
                follow_up_questions.append(f"Do you currently reside in a {target_loc} region?")
            elif (rule.rural_only and user_rural) or (not rule.rural_only and not user_rural):
                passed_rules_count += 1
                loc_name = "Rural" if user_rural else "Urban"
                satisfied_criteria.append(f"Area requirement matched: Resident of {loc_name} area")
            else:
                target_loc = "Rural" if rule.rural_only else "Urban"
                user_loc = "Urban" if user_rural is False else "Rural"
                unmet_criteria.append(f"Area mismatch: Designed for {target_loc} residents (Your profile: {user_loc})")

        # 8. Agricultural Landholding Check
        if rule.requires_landholding:
            total_rules_checked += 1
            land = p.get("landholding_acres")
            if land is None:
                unknown_criteria.append("Agricultural landholding status not recorded in profile")
                follow_up_questions.append("Do you own cultivable agricultural land, and what is the acreage?")
            elif land > 0:
                if rule.max_landholding_acres is None or land <= rule.max_landholding_acres:
                    passed_rules_count += 1
                    satisfied_criteria.append(f"Landholding verified: {land} acres (Small/marginal farm limit satisfied)")
                else:
                    unmet_criteria.append(f"Landholding exceeds threshold: {land} acres exceeds limit of {rule.max_landholding_acres} acres")
            else:
                unmet_criteria.append("Requires cultivable agricultural land in applicant's name")

        # 9. BPL / Priority Ration Card Requirement
        if rule.bpl_required:
            total_rules_checked += 1
            has_bpl = p.get("has_bpl_card")
            if has_bpl:
                passed_rules_count += 1
                satisfied_criteria.append("Priority economic status verified (BPL / Antyodaya ration card)")
            elif user_income is not None and user_income <= 150000:
                passed_rules_count += 1
                satisfied_criteria.append("Income qualification aligns with BPL economic criteria")
            elif has_bpl is None and user_income is None:
                unknown_criteria.append("Below Poverty Line (BPL) or priority ration card verification needed")
                follow_up_questions.append("Do you possess a BPL / Priority Ration Card or SECC record?")
            else:
                unmet_criteria.append("Requires Below Poverty Line (BPL) or eligible priority ration card")

        # 10. Student Requirement
        if rule.student_only:
            total_rules_checked += 1
            is_student_user = p.get("is_student") or ("student" in (p.get("occupation") or "").lower())
            if is_student_user:
                passed_rules_count += 1
                satisfied_criteria.append("Enrolled student qualification satisfied")
            elif p.get("is_student") is None and not user_occ:
                unknown_criteria.append("Requires active student enrollment in recognised institution")
                follow_up_questions.append("Are you currently enrolled as a student in a school, college, or university?")
            else:
                unmet_criteria.append("Scheme is reserved for currently enrolled students")

        # 11. Disability Requirement
        if rule.disability_required:
            total_rules_checked += 1
            is_dis = p.get("is_disabled")
            if is_dis:
                passed_rules_count += 1
                satisfied_criteria.append("Person with Disability (PwD) qualification matched")
            elif is_dis is None:
                unknown_criteria.append("Disability certificate verification needed")
                follow_up_questions.append("Do you hold a government-issued Unique Disability ID (UDID)?")
            else:
                unmet_criteria.append("Scheme is reserved for Persons with Disabilities (PwD)")

        # Compile Structured Results
        # Rules of evaluation:
        # - If there is ANY unmet hard condition -> conditions_not_met
        # - Else if there are unknown essential conditions -> more_info_required
        # - Else all known rules are passed -> likely_eligible
        if len(unmet_criteria) > 0:
            status = cls.STATUS_CONDITIONS_NOT_MET
            status_label = cls.LABEL_MAP[status]
            score = max(15, 45 - (len(unmet_criteria) * 10))
            summary = f"Profile does not meet {len(unmet_criteria)} criterion: {unmet_criteria[0]}."
            action_tip = "Explore alternative programs suited for your demographic and category."
        elif len(unknown_criteria) > 0:
            status = cls.STATUS_MORE_INFO_REQUIRED
            status_label = cls.LABEL_MAP[status]
            score = 65
            summary = f"You satisfy {len(satisfied_criteria)} verified rules, but {len(unknown_criteria)} criteria need confirmation: {unknown_criteria[0]}."
            action_tip = "Answer the follow-up question or update your profile to confirm eligibility."
        else:
            status = cls.STATUS_LIKELY_ELIGIBLE
            status_label = cls.LABEL_MAP[status]
            score = min(98, 85 + (passed_rules_count * 3))
            summary = "You satisfy all recorded eligibility criteria in your profile."
            action_tip = "Prepare your documents and proceed to apply via the official portal."

        required_docs = [
            {"name": d.document_name, "mandatory": d.is_mandatory, "notes": d.notes}
            for d in scheme.documents
        ] if scheme.documents else []

        return {
            "scheme_id": scheme.id,
            "scheme_name": scheme.name,
            "status": status,
            "status_label": status_label,
            "score": score,
            "satisfied_criteria": satisfied_criteria,
            "unmet_criteria": unmet_criteria,
            "unknown_criteria": unknown_criteria,
            "follow_up_questions": follow_up_questions,
            "required_documents": required_docs,
            # Backward-compatible fields
            "matched_rules": satisfied_criteria,
            "failed_rules": unmet_criteria,
            "neutral_rules": unknown_criteria,
            "summary_reason": summary,
            "action_tip": action_tip,
            "disclaimer": DISCLAIMER_TEXT
        }
