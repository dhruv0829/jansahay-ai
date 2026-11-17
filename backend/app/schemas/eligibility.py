from typing import Optional, List
from pydantic import BaseModel
from app.schemas.profile import ProfileBase

class EligibilityCheckRequest(BaseModel):
    scheme_id: Optional[int] = None
    profile: Optional[ProfileBase] = None

class EligibilityRuleMatch(BaseModel):
    rule_name: str
    status: str # "matched", "failed", "neutral", "unknown"
    detail: str

class SchemeEligibilityReport(BaseModel):
    scheme_id: int
    scheme_name: str
    status: str # "likely_eligible", "possibly_eligible", "not_eligible"
    status_label: str
    score: int
    matched_rules: List[str]
    failed_rules: List[str]
    neutral_rules: List[str] = []
    summary_reason: str
    action_tip: Optional[str] = None
