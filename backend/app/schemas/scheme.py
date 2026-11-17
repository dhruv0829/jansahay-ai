from typing import Optional, List, Any
import datetime
from pydantic import BaseModel

class SchemeBenefitOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    title_hindi: Optional[str] = None
    description_hindi: Optional[str] = None
    order_index: int = 0

    class Config:
        from_attributes = True

class SchemeDocumentOut(BaseModel):
    id: int
    document_name: str
    document_name_hindi: Optional[str] = None
    is_mandatory: bool = True
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class SchemeQAOut(BaseModel):
    id: int
    question_english: str
    question_hindi: Optional[str] = None
    answer_english: str
    answer_hindi: Optional[str] = None
    category: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[str] = None

    class Config:
        from_attributes = True

class EligibilityRuleOut(BaseModel):
    id: int
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    allowed_genders: Optional[str] = "All"
    allowed_occupations: Optional[str] = "All"
    max_annual_income: Optional[float] = None
    min_annual_income: Optional[float] = None
    allowed_states: Optional[str] = "All"
    allowed_categories: Optional[str] = "All"
    rural_only: Optional[bool] = None
    requires_landholding: Optional[bool] = None
    max_landholding_acres: Optional[float] = None
    disability_required: Optional[bool] = None
    bpl_required: Optional[bool] = None
    student_only: Optional[bool] = None
    custom_criteria_text: Optional[str] = None

    class Config:
        from_attributes = True

class SchemeBase(BaseModel):
    slug: str
    name: str
    short_name: Optional[str] = None
    department: str
    ministry: Optional[str] = None
    level: str = "Central"
    applicable_states: str = "All"
    category: str
    summary: str
    summary_hindi: Optional[str] = None
    description: str
    description_hindi: Optional[str] = None
    target_beneficiary: Optional[str] = None
    benefit_type: str
    benefit_amount: str
    application_mode: str = "Online"
    application_process: Optional[str] = None
    application_process_hindi: Optional[str] = None
    official_url: Optional[str] = None
    portal_name: Optional[str] = None
    launched_year: Optional[str] = None
    source_dataset: Optional[str] = "indian_government_schemes_dataset_english_and_hindi.csv"
    source_row_count: Optional[int] = 0
    aliases: Optional[str] = None
    is_active: bool = True
    is_verified: bool = True
    last_verified_date: Optional[str] = "October 2026"

class SchemeCreate(SchemeBase):
    pass

class SchemeOut(SchemeBase):
    id: int
    benefits_count: int = 0
    documents_count: int = 0
    qa_count: int = 0

    class Config:
        from_attributes = True

class SchemeDetailOut(SchemeBase):
    id: int
    benefits: List[SchemeBenefitOut] = []
    documents: List[SchemeDocumentOut] = []
    eligibility_rules: Optional[EligibilityRuleOut] = None
    qa_records: List[SchemeQAOut] = []

    class Config:
        from_attributes = True

class SchemeConflictOut(BaseModel):
    id: int
    scheme_name: str
    variant_name: str
    conflict_type: str
    resolution: str
    status: str
    details: Optional[str] = None

    class Config:
        from_attributes = True

class RecommendationOut(BaseModel):
    scheme: SchemeDetailOut
    match_score: int
    eligibility_status: str # "likely_eligible", "possibly_eligible", "not_eligible"
    status_label: str
    match_reasons: List[str]
    missing_criteria: List[str] = []
    score_breakdown: dict = {}

class DocumentUploadOut(BaseModel):
    id: int
    document_type: str
    original_filename: str
    file_size: int
    mime_type: str
    ocr_status: str
    confidence_score: float
    is_verified_by_user: bool
    extracted_data: Optional[str] = None
    verified_data: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True
