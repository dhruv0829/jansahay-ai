import os
import sys
import pytest

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.ocr_service import DocumentOCRService

def test_income_certificate_entity_extraction():
    sample_text = """
    GOVERNMENT OF MAHARASHTRA
    OFFICE OF THE TAHSILDAR, NASHIK
    INCOME CERTIFICATE
    Certificate No: MH2026/INC/9876543
    This is to certify that Shri Rameshwar Patil, resident of Niphad, Nashik, Maharashtra.
    Annual Income from all sources is Rs. 1,80,000/- (Rupees One Lakh Eighty Thousand only).
    Date of Issue: 12/03/2026
    """

    res = DocumentOCRService.parse_fields_from_text(sample_text, doc_type_hint="Income Certificate")
    assert res["detected_type"] == "Income Certificate"
    assert res["extracted_fields"].get("annual_income") == 180000.0
    assert res["extracted_fields"].get("state") == "Maharashtra"
    assert "certificate_identifier" in res["extracted_fields"]
    # Check that sensitive identifier is masked for privacy
    assert "*" in res["extracted_fields"]["certificate_identifier"]
    assert res["overall_confidence"] >= 0.85

def test_caste_certificate_extraction():
    sample_text = """
    OFFICE OF THE SUB-DIVISIONAL MAGISTRATE
    CASTE CERTIFICATE
    This is to certify that Smt. Anita Devi belongs to the Other Backward Class (OBC) category
    under Government Resolution No. BC/109/2024.
    State: Uttar Pradesh
    """

    res = DocumentOCRService.parse_fields_from_text(sample_text, doc_type_hint="Caste Certificate")
    assert res["detected_type"] == "Caste Certificate"
    assert res["extracted_fields"].get("social_category") == "OBC"
    assert res["extracted_fields"].get("state") == "Uttar Pradesh"

def test_land_record_extraction():
    sample_text = """
    REVENUE DEPARTMENT
    7/12 EXTRACT / KHATAUNI
    Village: Pimpalgaon, District: Nashik, Maharashtra
    Cultivable Agricultural Landholding: 2.50 Acres
    Soil Classification: Bagayat / Jirayat
    """

    res = DocumentOCRService.parse_fields_from_text(sample_text, doc_type_hint="Land Record / Khatauni")
    assert res["detected_type"] == "Land Record / Khatauni"
    assert res["extracted_fields"].get("landholding_acres") == 2.50
    assert res["extracted_fields"].get("state") == "Maharashtra"
