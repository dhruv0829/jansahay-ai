import os
import re
import uuid
from typing import Dict, Any, Optional, Tuple, List

class DocumentOCRService:
    """
    Intelligent Civic Document OCR and Entity Extraction Service.
    Extracts structured fields from Indian administrative certificates:
    - Income Certificate (वार्षिक आय प्रमाण पत्र)
    - Caste Certificate (जाति प्रमाण पत्र)
    - Land Record / 7/12 Extract / Khatauni (भूमि अभिलेख)
    - Ration Card (राशन कार्ड)
    - Identity Proof / Domicile (पहचान / अधिवास प्रमाण पत्र)
    """

    STATE_NAMES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi"
    ]

    SOCIAL_CATEGORIES = ["SC", "ST", "OBC", "EWS", "General", "VJNT", "NT", "SBC"]

    @classmethod
    def extract_text_from_file(cls, file_path: str, mime_type: str) -> str:
        """Extract raw text from uploaded document."""
        if not os.path.exists(file_path):
            return ""

        # Plain text
        if "text" in mime_type:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return ""

        # Extract embedded text from digital PDFs before attempting OCR.
        if mime_type == "application/pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if pdf_text.strip():
                    return pdf_text
            except Exception:
                pass

            # Scanned PDFs have no embedded text; render each page and OCR it.
            try:
                import pypdfium2 as pdfium
                import pytesseract
                pdf_doc = pdfium.PdfDocument(file_path)
                pages = []
                for page_index in range(min(len(pdf_doc), 20)):
                    page = pdf_doc[page_index]
                    bitmap = page.render(scale=2)
                    pages.append(pytesseract.image_to_string(bitmap.to_pil(), lang="eng+hin+mar"))
                pdf_doc.close()
                return "\n".join(pages).strip()
            except Exception:
                return ""

        # For images or PDFs
        raw_text = ""
        try:
            from PIL import Image
            img = Image.open(file_path)
            # Try pytesseract if installed
            try:
                import pytesseract
                raw_text = pytesseract.image_to_string(img, lang="eng+hin+mar")
            except Exception:
                raw_text = ""
        except Exception:
            pass

        # If image OCR wasn't able to run, inspect file metadata or read bytes as string
        if not raw_text:
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    # Extract printable ascii strings if any
                    ascii_strings = re.findall(rb'[a-zA-Z0-9\s,./\-\:]{4,}', content)
                    raw_text = " ".join([s.decode('latin1', errors='ignore') for s in ascii_strings[:100]])
            except Exception:
                raw_text = ""

        return raw_text

    @classmethod
    def process_document(
        cls,
        file_path: str,
        mime_type: str,
        doc_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured fields with uncertainty indicators and confidence scoring.
        """
        raw_text = cls.extract_text_from_file(file_path, mime_type)
        return cls.parse_fields_from_text(raw_text, doc_type_hint)

    @classmethod
    def parse_fields_from_text(
        cls,
        text: str,
        doc_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        t = text.lower()
        extracted: Dict[str, Any] = {}
        confidences: Dict[str, float] = {}
        uncertainties: List[str] = []

        # 1. Detect Document Type
        detected_type = doc_type_hint or "General Document"
        if any(k in t for k in ["income", "annual income", "varshik aay", "tahsildar", "revenue officer", "income certificate"]):
            detected_type = "Income Certificate"
        elif any(k in t for k in ["caste", "jati", "scheduled caste", "scheduled tribe", "obc", "caste certificate"]):
            detected_type = "Caste Certificate"
        elif any(k in t for k in ["7/12", "khatauni", "khasra", "khatiyan", "land record", "acre", "hectare", "gat no"]):
            detected_type = "Land Record / Khatauni"
        elif any(k in t for k in ["ration card", "bpl", "antyodaya", "food security", "ration"]):
            detected_type = "Ration Card"

        extracted["document_type"] = detected_type
        confidences["document_type"] = 0.90 if doc_type_hint else 0.82

        # 2. Extract Annual Income
        # Match patterns like: Rs. 1,80,000 / INR 180000 / ₹1,50,000 / 2,40,000/-
        income_match = re.search(r'(?:rs\.?|inr|₹|income(?:\s+is|\s+of)?|amount)\s*[:=-]?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{2})?|[0-9]{4,7})', t)
        if income_match:
            try:
                num_str = income_match.group(1).replace(",", "")
                income_val = float(num_str)
                if 10000 <= income_val <= 10000000:
                    extracted["annual_income"] = income_val
                    confidences["annual_income"] = 0.88
            except ValueError:
                pass

        if "annual_income" not in extracted and detected_type == "Income Certificate":
            uncertainties.append("Annual income figure could not be automatically extracted with high certainty.")

        # 3. Extract Social Category (SC, ST, OBC, EWS, General)
        for cat in cls.SOCIAL_CATEGORIES:
            pattern = r'\b' + re.escape(cat.lower()) + r'\b'
            if re.search(pattern, t):
                extracted["social_category"] = cat
                confidences["social_category"] = 0.92
                break

        if "social_category" not in extracted and detected_type == "Caste Certificate":
            uncertainties.append("Social category requires citizen review.")

        # 4. Extract Landholding Acres
        land_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:acres?|acre|hec|hectares?|guntha)', t)
        if land_match:
            try:
                val = float(land_match.group(1))
                if "hec" in land_match.group(0):
                    val = round(val * 2.471, 2) # convert hectare to acres
                extracted["landholding_acres"] = val
                confidences["landholding_acres"] = 0.85
            except ValueError:
                pass

        # 5. Extract State & District
        for st in cls.STATE_NAMES:
            if st.lower() in t:
                extracted["state"] = st
                confidences["state"] = 0.95
                break

        # 6. Extract Certificate / Document Identifier (masked for privacy)
        id_match = re.search(r'\b([A-Z]{2}[0-9A-Z\/\-]{6,16})\b', text)
        if id_match:
            raw_id = id_match.group(1)
            # Mask middle characters for privacy
            if len(raw_id) > 6:
                masked_id = raw_id[:3] + ("*" * (len(raw_id) - 5)) + raw_id[-2:]
            else:
                masked_id = raw_id
            extracted["certificate_identifier"] = masked_id
            confidences["certificate_identifier"] = 0.90

        # Overall document confidence
        overall_conf = round(sum(confidences.values()) / max(1, len(confidences)), 2) if confidences else 0.70

        return {
            "detected_type": detected_type,
            "extracted_fields": extracted,
            "field_confidences": confidences,
            "overall_confidence": overall_conf,
            "uncertainty_indicators": uncertainties,
            "requires_user_confirmation": True,
            "raw_text_snippet": (text[:250] + "...") if text else "No printable text detected in document layout."
        }
