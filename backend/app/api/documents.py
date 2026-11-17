import os
import json
import uuid
import shutil
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User, UserProfile, DocumentUpload, AuditLog, Scheme
from app.services.auth_service import get_current_user
from app.services.ocr_service import DocumentOCRService
from app.recommendation.engine import RecommendationEngine

router = APIRouter(prefix="/documents", tags=["Document Center & Intelligence"])

# Secure private storage directory
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "documents")
os.makedirs(STORAGE_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".txt"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB


def _file_signature_matches(extension: str, header: bytes) -> bool:
    signatures = {
        ".pdf": lambda data: data.startswith(b"%PDF-"),
        ".png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
        ".jpg": lambda data: data.startswith(b"\xff\xd8\xff"),
        ".jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
        ".webp": lambda data: len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP",
        ".txt": lambda data: b"\x00" not in data,
    }
    return signatures[extension](header)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure Document Upload & OCR Processing Endpoint.
    Validates file type, size, authorization; extracts civic fields with confidence indicators.
    """
    # 1. Validate file extension
    original_filename = os.path.basename(file.filename or "")[:255]
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, PNG, JPG, JPEG, WEBP, TXT."
        )

    # 2. Stream into private storage with a strict byte limit so an oversized
    # request cannot be fully buffered in application memory.
    secure_filename = f"{uuid.uuid4()}{ext}"
    destination_path = os.path.join(STORAGE_DIR, secure_filename)
    file_size = 0
    header = bytearray()
    try:
        with open(destination_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(status_code=413, detail="File size exceeds the 10 MB limit.")
                if len(header) < 16:
                    header.extend(chunk[:16 - len(header)])
                f.write(chunk)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if not _file_signature_matches(ext, bytes(header)):
            raise HTTPException(status_code=400, detail="File contents do not match the selected file type.")
    except Exception:
        if os.path.exists(destination_path):
            os.remove(destination_path)
        raise
    finally:
        await file.close()

    # 4. Perform OCR & Entity Extraction
    mime_type = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".txt": "text/plain",
    }[ext]
    ocr_result = DocumentOCRService.process_document(
        file_path=destination_path,
        mime_type=mime_type,
        doc_type_hint=document_type
    )
    ocr_status = "Completed" if ocr_result["raw_text_snippet"] != "No printable text detected in document layout." else "Failed"

    # 5. Persist Document Upload Record
    doc_rec = DocumentUpload(
        user_id=current_user.id,
        document_type=ocr_result["detected_type"],
        original_filename=original_filename,
        stored_filename=secure_filename,
        file_path=destination_path,
        file_size=file_size,
        mime_type=mime_type,
        ocr_status=ocr_status,
        raw_text=ocr_result["raw_text_snippet"],
        extracted_data=json.dumps(ocr_result["extracted_fields"]),
        confidence_score=ocr_result["overall_confidence"],
        is_verified_by_user=False,
        verified_data=None
    )
    db.add(doc_rec)
    db.flush()

    # 6. Audit Logging
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_UPLOAD",
        entity_type="DocumentUpload",
        entity_id=str(doc_rec.id),
        details=json.dumps({
            "original_name": file.filename,
            "document_type": ocr_result["detected_type"],
            "confidence": ocr_result["overall_confidence"]
        })
    )
    db.add(audit)
    db.commit()
    db.refresh(doc_rec)

    return {
        "id": doc_rec.id,
        "message": "Document uploaded. Please review and confirm extracted values." if ocr_status == "Completed" else "Document uploaded, but text could not be extracted. Please enter the details manually.",
        "ocr_status": ocr_status,
        "document_type": doc_rec.document_type,
        "original_filename": doc_rec.original_filename,
        "file_size": doc_rec.file_size,
        "confidence_score": doc_rec.confidence_score,
        "extracted_fields": ocr_result["extracted_fields"],
        "field_confidences": ocr_result["field_confidences"],
        "uncertainty_indicators": ocr_result["uncertainty_indicators"],
        "requires_user_confirmation": True
    }

@router.get("")
def list_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents uploaded by the authenticated citizen."""
    docs = db.query(DocumentUpload).filter(DocumentUpload.user_id == current_user.id).order_by(DocumentUpload.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "document_type": d.document_type,
            "original_filename": d.original_filename,
            "file_size": d.file_size,
            "ocr_status": d.ocr_status,
            "confidence_score": d.confidence_score,
            "is_verified_by_user": d.is_verified_by_user,
            "extracted_fields": json.loads(d.extracted_data) if d.extracted_data else {},
            "verified_fields": json.loads(d.verified_data) if d.verified_data else {},
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

@router.post("/{doc_id}/confirm")
def confirm_extracted_data(
    doc_id: int,
    confirmed_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm and apply extracted document values to citizen profile.
    Re-evaluates eligibility and returns personalized recommendations.
    """
    doc = db.query(DocumentUpload).filter(
        DocumentUpload.id == doc_id,
        DocumentUpload.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")

    # 1. Update Document Record
    doc.is_verified_by_user = True
    doc.verified_data = json.dumps(confirmed_data)

    # 2. Pass confirmed information into User Profile
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()

    updated_fields = []
    if "annual_income" in confirmed_data and confirmed_data["annual_income"] is not None:
        try:
            profile.annual_income = float(confirmed_data["annual_income"])
            updated_fields.append("annual_income")
        except ValueError:
            pass

    if "social_category" in confirmed_data and confirmed_data["social_category"]:
        profile.social_category = str(confirmed_data["social_category"])
        updated_fields.append("social_category")

    if "landholding_acres" in confirmed_data and confirmed_data["landholding_acres"] is not None:
        try:
            profile.landholding_acres = float(confirmed_data["landholding_acres"])
            updated_fields.append("landholding_acres")
        except ValueError:
            pass

    if "state" in confirmed_data and confirmed_data["state"]:
        profile.state = str(confirmed_data["state"])
        updated_fields.append("state")

    # 3. Log Audit
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_CONFIRMED",
        entity_type="DocumentUpload",
        entity_id=str(doc.id),
        details=json.dumps({"confirmed_fields": updated_fields})
    )
    db.add(audit)
    db.commit()
    db.refresh(profile)

    # 4. Generate refreshed scheme recommendations
    schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
    recommendations = RecommendationEngine.rank_schemes(schemes, profile, limit=4)

    return {
        "status": "success",
        "message": f"Document data confirmed and {len(updated_fields)} profile fields verified successfully.",
        "updated_profile_fields": updated_fields,
        "verified_data": confirmed_data,
        "recommendations": recommendations,
        "explanation": (
            f"Your confirmed {', '.join(updated_fields)} from {doc.document_type} "
            f"have been verified and applied to compute your latest scheme eligibility."
        )
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure Document Deletion Endpoint.
    Purges file from private disk storage, removes database record, and logs audit trail.
    """
    doc = db.query(DocumentUpload).filter(DocumentUpload.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Authorization: Owner or Admin only
    if doc.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document.")

    # Purge file from private storage
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Warning: could not delete file {doc.file_path}: {e}")

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_DELETED",
        entity_type="DocumentUpload",
        entity_id=str(doc.id),
        details=json.dumps({"original_filename": doc.original_filename})
    )
    db.add(audit)

    db.delete(doc)
    db.commit()

    return {
        "status": "success",
        "message": f"Document '{doc.original_filename}' and associated private storage data deleted permanently."
    }
