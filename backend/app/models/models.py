import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database.session import Base, CREDENTIALS_SCHEMA, SCHEMES_SCHEMA


def _fk(schema, table, column):
    prefix = f"{schema}." if schema else ""
    return f"{prefix}{table}.{column}"


def _schema_args(schema):
    return {"schema": schema} if schema else {}

class User(Base):
    __tablename__ = "users"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications = relationship("ApplicationTrack", back_populates="user", cascade="all, delete-orphan")
    uploaded_documents = relationship("DocumentUpload", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(_fk(CREDENTIALS_SCHEMA, "users", "id")), unique=True, nullable=False)
    
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True) # Male, Female, Other
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True) # Farmer, Student, Self-Employed, Daily Wage, Artisan, Street Vendor, etc.
    annual_income = Column(Float, nullable=True)
    social_category = Column(String(50), nullable=True) # General, OBC, SC, ST, EWS
    is_rural = Column(Boolean, default=True)
    landholding_acres = Column(Float, default=0.0)
    is_disabled = Column(Boolean, default=False)
    has_bpl_card = Column(Boolean, default=False)
    is_student = Column(Boolean, default=False)
    education_level = Column(String(100), nullable=True) # 10th, 12th, Graduate, Post Graduate
    minority = Column(Boolean, default=False)
    preferred_language = Column(String(10), default="en") # en, hi, mr
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Scheme(Base):
    __tablename__ = "schemes"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(100), nullable=True)
    department = Column(String(255), nullable=False)
    ministry = Column(String(255), nullable=True)
    level = Column(String(50), default="Central") # Central, State
    applicable_states = Column(String(500), default="All") # "All" or comma-separated list
    category = Column(String(100), nullable=False, index=True) # Agriculture, Healthcare, Education, etc.
    summary = Column(Text, nullable=False)
    summary_hindi = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    description_hindi = Column(Text, nullable=True)
    target_beneficiary = Column(String(255), nullable=True)
    benefit_type = Column(String(100), nullable=False) # Direct Cash Transfer, Subsidy, Insurance, Loan, Scholarship, etc.
    benefit_amount = Column(String(255), nullable=False) # e.g. "₹6,000 / year", "Up to ₹5 Lakh/year cashless hospital cover"
    application_mode = Column(String(50), default="Online") # Online, Offline, Both
    application_process = Column(Text, nullable=True)
    application_process_hindi = Column(Text, nullable=True)
    official_url = Column(String(500), nullable=True)
    portal_name = Column(String(255), nullable=True)
    launched_year = Column(String(50), nullable=True)
    source_dataset = Column(String(255), default="indian_government_schemes_dataset_english_and_hindi.csv")
    source_row_count = Column(Integer, default=0)
    source_record_ids = Column(Text, nullable=True) # Comma-separated or JSON list of original CSV row indices
    aliases = Column(Text, nullable=True) # JSON list of alias names or variations
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_verified_date = Column(String(50), nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    eligibility_rules = relationship("EligibilityRule", back_populates="scheme", uselist=False, cascade="all, delete-orphan")
    benefits = relationship("SchemeBenefit", back_populates="scheme", cascade="all, delete-orphan")
    documents = relationship("SchemeDocument", back_populates="scheme", cascade="all, delete-orphan")
    applications = relationship("ApplicationTrack", back_populates="scheme", cascade="all, delete-orphan")
    qa_records = relationship("SchemeQA", back_populates="scheme", cascade="all, delete-orphan")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), unique=True, nullable=False)
    
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    allowed_genders = Column(String(100), default="All") # "All", "Female", "Male"
    allowed_occupations = Column(String(500), default="All") # Comma separated or "All"
    max_annual_income = Column(Float, nullable=True)
    min_annual_income = Column(Float, nullable=True)
    allowed_states = Column(String(500), default="All")
    allowed_categories = Column(String(200), default="All") # General, OBC, SC, ST, EWS
    rural_only = Column(Boolean, nullable=True) # True=rural, False=urban, None=both
    requires_landholding = Column(Boolean, nullable=True)
    max_landholding_acres = Column(Float, nullable=True)
    disability_required = Column(Boolean, nullable=True)
    bpl_required = Column(Boolean, nullable=True)
    student_only = Column(Boolean, nullable=True)
    custom_criteria_text = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="eligibility_rules")


class SchemeBenefit(Base):
    __tablename__ = "scheme_benefits"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    title_hindi = Column(String(255), nullable=True)
    description_hindi = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)

    scheme = relationship("Scheme", back_populates="benefits")


class SchemeDocument(Base):
    __tablename__ = "scheme_documents"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_name_hindi = Column(String(255), nullable=True)
    is_mandatory = Column(Boolean, default=True)
    notes = Column(String(255), nullable=True)

    scheme = relationship("Scheme", back_populates="documents")


class SchemeQA(Base):
    __tablename__ = "scheme_qa"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), nullable=False, index=True)
    question_english = Column(Text, nullable=False)
    question_hindi = Column(Text, nullable=True)
    answer_english = Column(Text, nullable=False)
    answer_hindi = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    topic = Column(String(100), nullable=True, index=True) # overview, eligibility, benefits, application_process, documents, etc.
    difficulty_level = Column(String(50), nullable=True)
    source_row_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scheme = relationship("Scheme", back_populates="qa_records")


class SchemeConflict(Base):
    __tablename__ = "scheme_conflicts"
    __table_args__ = _schema_args(SCHEMES_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    canonical_scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), nullable=True)
    scheme_name = Column(String(255), nullable=False)
    variant_name = Column(String(255), nullable=False)
    conflict_type = Column(String(100), nullable=False) # name_variant, alias_merged, field_mismatch
    resolution = Column(String(100), default="Merged into canonical scheme")
    details = Column(Text, nullable=True) # JSON string
    status = Column(String(50), default="Resolved") # Resolved, Pending Review
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ApplicationTrack(Base):
    __tablename__ = "application_tracks"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(_fk(CREDENTIALS_SCHEMA, "users", "id")), nullable=False)
    scheme_id = Column(Integer, ForeignKey(_fk(SCHEMES_SCHEMA, "schemes", "id")), nullable=False)
    status = Column(String(50), default="Saved") # Saved, In Progress, Submitted, Approved, Rejected
    notes = Column(Text, nullable=True)
    applied_date = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")


class DocumentUpload(Base):
    __tablename__ = "document_uploads"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(_fk(CREDENTIALS_SCHEMA, "users", "id")), nullable=False, index=True)
    document_type = Column(String(100), nullable=False) # Income Certificate, Caste Certificate, Land Record, Identity Proof, Ration Card
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    ocr_status = Column(String(50), default="Completed") # Processing, Completed, Failed
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True) # JSON string with detected fields (annual_income, social_category, landholding_acres, etc.)
    confidence_score = Column(Float, default=0.88)
    is_verified_by_user = Column(Boolean, default=False)
    verified_data = Column(Text, nullable=True) # JSON string after citizen review/confirmation
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="uploaded_documents")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(_fk(CREDENTIALS_SCHEMA, "users", "id")), nullable=True)
    action = Column(String(100), nullable=False) # DATASET_IMPORT, SCHEME_VERIFIED, DOCUMENT_UPLOAD, DOCUMENT_DELETED, etc.
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_histories"
    __table_args__ = _schema_args(CREDENTIALS_SCHEMA)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(_fk(CREDENTIALS_SCHEMA, "users", "id")), nullable=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False) # user / assistant
    content = Column(Text, nullable=False)
    structured_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
