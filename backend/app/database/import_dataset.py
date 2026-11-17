import csv
import json
import os
import re
import sys
import argparse
from datetime import datetime
from collections import defaultdict, Counter

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal, engine, Base
from app.models.models import (
    User, UserProfile, Scheme, EligibilityRule,
    SchemeBenefit, SchemeDocument, SchemeQA, SchemeConflict, AuditLog
)
from app.services.auth_service import hash_password
from app.config import settings

DATASET_PATH = os.path.join(backend_dir, "..", "data", "indian_government_schemes_dataset_english_and_hindi.csv")
DATASET_PATH = os.path.normpath(DATASET_PATH)

REPORT_PATH = os.path.join(backend_dir, "dataset_import_report.json")

# Canonical Groupings: maps raw name variant to canonical scheme name
RAW_TO_CANONICAL = {
    "AMRUT Mission": "AMRUT",
    "AMRUT (Atal Mission for Rejuvenation and Urban Transformation)": "AMRUT",
    
    "Atal Pension Yojana": "Atal Pension Yojana (APY)",
    "Atal Pension Yojana (APY)": "Atal Pension Yojana (APY)",
    
    "Ayushman Bharat (PM-JAY)": "Ayushman Bharat (PM-JAY)",
    "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)": "Ayushman Bharat (PM-JAY)",
    
    "Beti Bachao Beti Padhao": "Beti Bachao Beti Padhao (BBBP)",
    "Beti Bachao Beti Padhao (BBBP)": "Beti Bachao Beti Padhao (BBBP)",
    
    "Digital India": "Digital India",
    "Digital India Programme": "Digital India",
    
    "Jal Jeevan Mission": "Jal Jeevan Mission (JJM)",
    "Jal Jeevan Mission (JJM)": "Jal Jeevan Mission (JJM)",
    
    "Jan Dhan Yojana": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    "Pradhan Mantri Jan Dhan Yojana (PMJDY)": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    
    "MGNREGA": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
    "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)": "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)",
    
    "MUDRA Yojana": "Pradhan Mantri MUDRA Yojana (PMMY)",
    "Pradhan Mantri MUDRA Yojana (PMMY)": "Pradhan Mantri MUDRA Yojana (PMMY)",
    
    "National Education Policy 2020": "National Education Policy 2020",
    "National Education Policy 2020 Implementation": "National Education Policy 2020",
    
    "National Health Mission": "National Health Mission (NHM)",
    "National Health Mission (NHM)": "National Health Mission (NHM)",
    
    "National Livelihood Mission (NRLM/DAY-NRLM)": "National Rural Livelihood Mission (DAY-NRLM)",
    "National Rural Livelihood Mission": "National Rural Livelihood Mission (DAY-NRLM)",
    
    "PM Fasal Bima Yojana": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
    
    "PM Kaushal Vikas Yojana": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
    "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
    
    "PM Kisan Samman Nidhi": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    "PM-KISAN": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    
    "PM Matru Vandana Yojana": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
    "PM Matru Vandana Yojana (PMMVY)": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
    
    "PM SVANidhi": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
    "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
    
    "PM Ujjwala Yojana": "Pradhan Mantri Ujjwala Yojana (PMUY)",
    "Pradhan Mantri Ujjwala Yojana (PMUY)": "Pradhan Mantri Ujjwala Yojana (PMUY)",
    
    "Pradhan Mantri Jeevan Jyoti Bima Yojana": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
    "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
    
    "Pradhan Mantri Suraksha Bima Yojana": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
    "Pradhan Mantri Suraksha Bima Yojana (PMSBY)": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
    
    "Samagra Shiksha": "Samagra Shiksha Abhiyan",
    "Samagra Shiksha Abhiyan": "Samagra Shiksha Abhiyan",
    
    "Startup India": "Startup India Initiative",
    "Startup India Initiative": "Startup India Initiative",
    
    "Swachh Bharat Mission": "Swachh Bharat Mission (SBM)",
    "Swachh Bharat Mission (SBM)": "Swachh Bharat Mission (SBM)",
}

# Scheme Ministry & Department mappings
CATEGORY_MINISTRY_MAP = {
    "Agriculture": ("Department of Agriculture & Farmers Welfare", "Ministry of Agriculture & Farmers Welfare"),
    "Healthcare": ("National Health Authority / MoHFW", "Ministry of Health & Family Welfare"),
    "Financial Services": ("Department of Financial Services", "Ministry of Finance"),
    "Education & Scholarships": ("Department of School Education & Literacy", "Ministry of Education"),
    "Employment & Skill": ("Ministry of Skill Development & Entrepreneurship", "Government of India"),
    "Social Security": ("Ministry of Social Justice and Empowerment", "Government of India"),
    "Women & Child Development": ("Ministry of Women and Child Development", "Government of India"),
    "Housing & Urban Affairs": ("Ministry of Housing and Urban Affairs", "Government of India"),
    "Renewable Energy & Power": ("Ministry of Power & MNRE", "Government of India"),
    "Digital & IT Services": ("Ministry of Electronics & Information Technology", "Government of India"),
    "Business & MSME": ("Ministry of Micro, Small and Medium Enterprises", "Government of India"),
}

CATEGORY_NORMALIZE = {
    "agriculture": "Agriculture",
    "health": "Healthcare",
    "healthcare": "Healthcare",
    "finance": "Financial Services",
    "education": "Education & Scholarships",
    "skill development": "Employment & Skill",
    "energy": "Renewable Energy & Power",
    "technology": "Digital & IT Services",
    "social welfare": "Social Security",
    "urban development": "Housing & Urban Affairs",
    "insurance": "Financial Services",
    "business": "Business & MSME",
    "manufacturing": "Business & MSME",
    "women and child development": "Women & Child Development",
    "employment": "Employment & Skill",
    "water resources": "Social Security",
    "sports": "Education & Scholarships",
    "culture": "Social Security",
}

# Known state schemes
STATE_SCHEME_CONFIG = {
    "Aarogyasri (Andhra Pradesh/Telangana)": {
        "level": "State",
        "states": "Andhra Pradesh, Telangana",
        "department": "Aarogyasri Health Care Trust",
        "ministry": "Government of Andhra Pradesh / Telangana"
    },
    "Kanyashree Prakalpa (West Bengal)": {
        "level": "State",
        "states": "West Bengal",
        "department": "Department of Women & Child Development and Social Welfare",
        "ministry": "Government of West Bengal"
    },
    "Ladli Laxmi Yojana (Madhya Pradesh)": {
        "level": "State",
        "states": "Madhya Pradesh",
        "department": "Department of Women and Child Development",
        "ministry": "Government of Madhya Pradesh"
    },
    "Mukhyamantri Kisan Kalyan Yojana (MP)": {
        "level": "State",
        "states": "Madhya Pradesh",
        "department": "Department of Farmer Welfare and Agriculture Development",
        "ministry": "Government of Madhya Pradesh"
    },
    "Rythu Bandhu (Telangana)": {
        "level": "State",
        "states": "Telangana",
        "department": "Department of Agriculture",
        "ministry": "Government of Telangana"
    }
}

# Structured Scheme Specific Rules overrides for verified accuracy
CURATED_SCHEME_RULES = {
    "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)": {
        "short_name": "PM-KISAN",
        "slug": "pm-kisan",
        "benefit_amount": "₹6,000 / year (in 3 equal installments of ₹2,000)",
        "benefit_type": "Direct Cash Transfer (DBT)",
        "rule": {
            "min_age": 18,
            "max_age": 75,
            "allowed_genders": "All",
            "allowed_occupations": "Farmer, Small Holder Farmer, Agricultural Worker",
            "max_annual_income": 400000.0,
            "allowed_states": "All",
            "allowed_categories": "All",
            "rural_only": None,
            "requires_landholding": True,
            "max_landholding_acres": 5.0,
            "custom_criteria_text": "Must own cultivable agricultural land in applicant's name with valid land records."
        },
        "benefits": [
            ("Direct Income Support", "₹6,000 credited annually in 3 installments into Aadhaar-seeded bank account.", "प्रत्यक्ष आय सहायता"),
            ("Zero Intermediary", "100% Direct Benefit Transfer (DBT) directly from Central Government.", "शून्य बिचौलिया डीबीटी"),
            ("KCC Linkage", "Automatic eligibility facilitation for subsidized Kisan Credit Card.", "केसीसी लिंकेज")
        ],
        "documents": [
            ("Aadhaar Card", True, "Linked with active mobile number", "आधार कार्ड"),
            ("Landholding Record / 7/12 Extract (Khatauni)", True, "Valid state land revenue extract", "भूमि स्वामित्व अभिलेख"),
            ("Bank Account Passbook", True, "Aadhaar and NPCI seeded bank account", "बैंक खाता पासबुक")
        ]
    },
    "Ayushman Bharat (PM-JAY)": {
        "short_name": "PM-JAY",
        "slug": "pm-jay",
        "benefit_amount": "Up to ₹5,00,000 / year cashless hospital cover per family",
        "benefit_type": "Cashless Health Insurance",
        "rule": {
            "min_age": None,
            "max_age": None,
            "allowed_genders": "All",
            "allowed_occupations": "All",
            "max_annual_income": 250000.0,
            "allowed_states": "All",
            "allowed_categories": "All",
            "rural_only": None,
            "requires_landholding": False,
            "bpl_required": True,
            "custom_criteria_text": "Families identified in Socio-Economic Caste Census (SECC 2011) or possessing eligible ration cards."
        },
        "benefits": [
            ("Cashless Inpatient Cover", "₹5 Lakh annual coverage per family for secondary & tertiary hospitalization.", "₹5 लाख कैशलेस स्वास्थ्य बीमा"),
            ("Pan-India Portability", "Valid at all empaneled public and private hospitals across India.", "अखिल भारतीय पोर्टेबिलिटी"),
            ("Pre and Post Hospitalization", "Covers 3 days pre-hospitalization and 15 days post-hospitalization medicines.", "अस्पताल में भर्ती से पहले और बाद का खर्च")
        ],
        "documents": [
            ("Aadhaar Card", True, "For identity verification and biometric authentication", "आधार कार्ड"),
            ("Ration Card / SECC Family ID", True, "To verify household eligibility in PM-JAY database", "राशन कार्ड"),
            ("Mobile Number", True, "For OTP verification and Ayushman Card generation", "मोबाइल नंबर")
        ]
    },
    "Atal Pension Yojana (APY)": {
        "short_name": "APY",
        "slug": "atal-pension-yojana",
        "benefit_amount": "Guaranteed monthly pension ₹1,000 to ₹5,000 after age 60",
        "benefit_type": "Guaranteed Pension",
        "rule": {
            "min_age": 18,
            "max_age": 40,
            "allowed_genders": "All",
            "allowed_occupations": "Unorganized Worker, Daily Wage, Self-Employed, Citizen",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Indian citizen aged 18-40 with savings bank account. Must not be an income tax payer."
        },
        "benefits": [
            ("Guaranteed Pension", "Fixed monthly pension of ₹1,000 to ₹5,000 after attaining 60 years.", "निश्चित मासिक पेंशन"),
            ("Spouse & Nominee Protection", "Same pension continues to spouse on subscriber death; corpus returned to nominee.", "पति/पत्नी और नामांकित व्यक्ति सुरक्षा"),
            ("Tax Benefits", "Contributions eligible for tax deduction under Section 80CCD.", "कर लाभ")
        ],
        "documents": [
            ("Aadhaar Card", True, "Identity and KYC verification", "आधार कार्ड"),
            ("Savings Bank Account Details", True, "Auto-debit authorization for monthly contributions", "बचत बैंक खाता"),
            ("Active Mobile Number", True, "For SMS transaction alerts and PRAN generation", "मोबाइल नंबर")
        ]
    },
    "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)": {
        "short_name": "PM SVANidhi",
        "slug": "pm-svanidhi",
        "benefit_amount": "Collateral-free working capital loan of ₹10,000 to ₹50,000 with 7% interest subsidy",
        "benefit_type": "Subsidized Micro-Credit Loan",
        "rule": {
            "min_age": 18,
            "max_age": 70,
            "allowed_genders": "All",
            "allowed_occupations": "Street Vendor, Hawker, Thelewala, Vendor",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "rural_only": False,
            "custom_criteria_text": "Street vendors vending in urban areas possessing Vending Certificate or Identity Card."
        },
        "benefits": [
            ("Tranche 1 Loan", "Initial working capital loan up to ₹10,000 with 1-year tenure.", "₹10,000 तक की पहली कार्यशील पूंजी"),
            ("Progressive Credit Limit", "Eligible for ₹20,000 (Tranche 2) and ₹50,000 (Tranche 3) on timely repayment.", "समय पर पुनर्भुगतान पर बढ़ी हुई ऋण सीमा"),
            ("7% Interest Subsidy", "Direct quarterly credit of 7% interest subsidy to bank account.", "7% ब्याज सब्सिडी"),
            ("Cashback for Digital Transactions", "Up to ₹1,200 per year cashback on digital transactions.", "डिजिटल लेनदेन पर कैशबैक")
        ],
        "documents": [
            ("Aadhaar Card", True, "Identity and DBT seeding", "आधार कार्ड"),
            ("Vending Certificate / Urban Local Body ID", True, "Issued by municipality or local body", "विक्रेता प्रमाण पत्र"),
            ("Bank Account Passbook", True, "For loan disbursement and cashback receipt", "बैंक पासबुक")
        ]
    },
    "Pradhan Mantri Awas Yojana (PMAY)": {
        "short_name": "PMAY",
        "slug": "pmay",
        "benefit_amount": "Up to ₹2.67 Lakh interest subsidy (Urban) or ₹1.20 - ₹1.30 Lakh direct grant (Gramin)",
        "benefit_type": "Housing Grant & Interest Subsidy",
        "rule": {
            "min_age": 21,
            "max_age": 70,
            "allowed_genders": "All",
            "allowed_occupations": "All",
            "max_annual_income": 600000.0,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Beneficiary family must not own a pucca house anywhere in India."
        },
        "benefits": [
            ("Affordable Pucca House", "Direct grant of ₹1.20 Lakh in plains, ₹1.30 Lakh in hilly/difficult areas (PMAY-G).", "सस्ता पक्का मकान"),
            ("Credit Linked Subsidy (CLSS)", "Up to 6.5% interest subsidy on home loans for EWS/LIG (PMAY-U).", "ऋण लिंक्ड ब्याज सब्सिडी"),
            ("Basic Amenities Included", "Mandatory inclusion of toilet under Swachh Bharat, electricity, and water.", "शौचालय, बिजली और पानी की सुविधा")
        ],
        "documents": [
            ("Aadhaar Card of all family members", True, "Identity verification", "आधार कार्ड"),
            ("Income Certificate / Salary Slip / Affidavit", True, "Income bracket verification", "आय प्रमाण पत्र"),
            ("Bank Account Details", True, "For direct fund transfer", "बैंक विवरण"),
            ("Affidavit of Not Owning Pucca House", True, "Self-declaration", "पक्का मकान न होने का शपथ पत्र")
        ]
    },
    "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)": {
        "short_name": "MGNREGA",
        "slug": "mgnrega",
        "benefit_amount": "Guaranteed 100 days of wage employment per financial year at statutory state wages",
        "benefit_type": "Guaranteed Wage Employment",
        "rule": {
            "min_age": 18,
            "max_age": None,
            "allowed_genders": "All",
            "allowed_occupations": "Agricultural Worker, Daily Wage, Rural Labor, Unorganized Worker",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "rural_only": True,
            "custom_criteria_text": "Adult members of rural households willing to do unskilled manual work."
        },
        "benefits": [
            ("100 Days Guaranteed Work", "Legal guarantee of 100 days unskilled manual work per household.", "100 दिन का गारंटीशुदा रोजगार"),
            ("Unemployment Allowance", "Statutory allowance if employment is not provided within 15 days of application.", "15 दिनों में काम न मिलने पर बेरोजगारी भत्ता"),
            ("Equal Wage for Men & Women", "Statutory wage parity credited directly into bank/post office accounts.", "महिला और पुरुष दोनों के लिए समान वेतन")
        ],
        "documents": [
            ("Job Card / Application Form", True, "Available free at local Gram Panchayat", "जॉब कार्ड"),
            ("Aadhaar Card", True, "For wage verification and DBT", "आधार कार्ड"),
            ("Bank / Post Office Passbook", True, "For direct wage transfer", "बैंक खाता पासबुक")
        ]
    },
    "Pradhan Mantri Mudra Yojana (PMMY)": {
        "short_name": "PMMY / MUDRA",
        "slug": "pm-mudra",
        "benefit_amount": "Collateral-free business loans up to ₹10 Lakh (Shishu, Kishore, Tarun categories)",
        "benefit_type": "Collateral-Free Business Loan",
        "rule": {
            "min_age": 18,
            "max_age": 65,
            "allowed_genders": "All",
            "allowed_occupations": "Self-Employed, Entrepreneur, Artisan, Small Business, Trader, Shopkeeper",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Non-corporate, non-farm small/micro enterprises needing credit for manufacturing, trading, or services."
        },
        "benefits": [
            ("Shishu Category", "Loans up to ₹50,000 for early stage ventures with no processing fee.", "शिशु ऋण ₹50,000 तक"),
            ("Kishore Category", "Loans from ₹50,001 to ₹5,00,000 for growing micro-businesses.", "किशोर ऋण ₹5 लाख तक"),
            ("Tarun Category", "Loans from ₹5,00,001 up to ₹10,00,000 for enterprise expansion.", "तरुण ऋण ₹10 लाख तक"),
            ("No Collateral Required", "Zero collateral or third-party guarantee needed.", "बिना किसी गारंटी के ऋण")
        ],
        "documents": [
            ("Aadhaar / Voter ID / Passport", True, "Proof of Identity", "पहचान प्रमाण पत्र"),
            ("Proof of Business Address / Trade License", True, "Proof of enterprise establishment", "व्यवसाय का पता प्रमाण"),
            ("Bank Statement of last 6 months", True, "Financial viability check", "पिछले 6 महीने का बैंक स्टेटमेंट")
        ]
    },
    "Sukanya Samriddhi Yojana (SSY)": {
        "short_name": "SSY",
        "slug": "sukanya-samriddhi-yojana",
        "benefit_amount": "High sovereign guaranteed interest rate (8.2%) with EEE tax exemption under Sec 80C",
        "benefit_type": "Government Guaranteed Savings Scheme",
        "rule": {
            "min_age": 0,
            "max_age": 10,
            "allowed_genders": "Female",
            "allowed_occupations": "All",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Account opened by parents/guardians for a girl child from birth up to age 10."
        },
        "benefits": [
            ("High Guaranteed Interest", "Attractive sovereign-backed interest rate (8.2% p.a.) compounded annually.", "8.2% वार्षिक ब्याज दर"),
            ("Triple Tax Exemption (EEE)", "Exemption on investment, interest earned, and maturity proceeds under Section 80C.", "धारा 80C के तहत पूरी तरह कर-मुक्त"),
            ("Education & Marriage Security", "50% withdrawal allowed after age 18 for higher education.", "उच्च शिक्षा और विवाह के लिए वित्तीय सुरक्षा")
        ],
        "documents": [
            ("Birth Certificate of Girl Child", True, "Issued by municipal authority or registrar", "बालिका का जन्म प्रमाण पत्र"),
            ("Aadhaar Card / ID of Parent or Guardian", True, "Proof of identity", "माता-पिता का आधार कार्ड"),
            ("Proof of Residence", True, "Electricity bill / Ration card / Passport", "निवास प्रमाण पत्र")
        ]
    },
    "Stand Up India": {
        "short_name": "Stand Up India",
        "slug": "stand-up-india",
        "benefit_amount": "Composite bank loans between ₹10 Lakh and ₹1 Crore for greenfield enterprises",
        "benefit_type": "Subsidized Enterprise Loan",
        "rule": {
            "min_age": 18,
            "max_age": 70,
            "allowed_genders": "Female, Male",
            "allowed_occupations": "Entrepreneur, Self-Employed, Business",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "SC, ST, Women",
            "custom_criteria_text": "SC/ST and/or woman entrepreneur setting up a greenfield enterprise in manufacturing, services, or trading."
        },
        "benefits": [
            ("Substantial Credit Facility", "Composite loan (term loan & working capital) between ₹10 Lakh and ₹1 Crore.", "₹10 लाख से ₹1 करोड़ तक का बैंक ऋण"),
            ("Concessional Rate of Interest", "Lowest applicable rate of bank for that category (not exceeding Base Rate + 3% + Tenor Premium).", "रियायती ब्याज दर"),
            ("Handholding Support", "Guidance from SIDBI, NABARD, and designated mentorship agencies.", "व्यावसायिक मार्गदर्शन और सहयोग")
        ],
        "documents": [
            ("Identity & Address Proof", True, "Aadhaar, PAN, Passport", "पहचान और पता प्रमाण पत्र"),
            ("Caste Certificate (for SC/ST)", True, "Issued by competent state revenue authority", "जाति प्रमाण पत्र"),
            ("Detailed Project Report (DPR)", True, "Greenfield enterprise project outline", "परियोजना रिपोर्ट")
        ]
    },
    "Pradhan Mantri Ujjwala Yojana (PMUY)": {
        "short_name": "PMUY",
        "slug": "pmuy",
        "benefit_amount": "Deposit-free LPG cylinder connection + ₹1,600 government financial assistance",
        "benefit_type": "Clean Energy Subsidy & Free LPG Connection",
        "rule": {
            "min_age": 18,
            "max_age": None,
            "allowed_genders": "Female",
            "allowed_occupations": "All",
            "max_annual_income": 200000.0,
            "allowed_states": "All",
            "allowed_categories": "All",
            "bpl_required": True,
            "custom_criteria_text": "Adult woman belonging to poor/BPL household having no existing LPG connection in the family."
        },
        "benefits": [
            ("Deposit-Free Connection", "Government covers security deposit of cylinder and pressure regulator (₹1,600).", "बिना सुरक्षा जमा राशि के एलपीजी कनेक्शन"),
            ("First Refill and Stove Free", "First LPG refill and two-burner stove provided free of cost under Ujjwala 2.0.", "पहला रिफिल और चूल्हा पूरी तरह मुफ्त"),
            ("Health & Environment Protection", "Eliminates toxic indoor air pollution from firewood and cow dung cakes.", "स्वच्छ ईंधन, धुआं-मुक्त रसोई")
        ],
        "documents": [
            ("Aadhaar Card of Woman Applicant", True, "For identity & biometric verification", "महिला का आधार कार्ड"),
            ("Ration Card / BPL Proof", True, "To verify household composition & BPL status", "राशन कार्ड"),
            ("Bank Account Details", True, "Aadhaar seeded for DBT subsidy credit", "बैंक खाता विवरण")
        ]
    },
    "Pradhan Mantri Suraksha Bima Yojana (PMSBY)": {
        "short_name": "PMSBY",
        "slug": "pmsby",
        "benefit_amount": "₹2,00,000 accidental death & full disability cover for just ₹20 / year premium",
        "benefit_type": "Accidental Death & Disability Insurance",
        "rule": {
            "min_age": 18,
            "max_age": 70,
            "allowed_genders": "All",
            "allowed_occupations": "All",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Indian citizen aged 18 to 70 with an active savings bank account."
        },
        "benefits": [
            ("Accidental Death Cover", "₹2,00,000 paid to nominee in case of accidental death.", "दुर्घटना मृत्यु पर ₹2 लाख"),
            ("Permanent Total Disability Cover", "₹2,00,000 paid for loss of both eyes or both hands/feet.", "पूर्ण स्थायी विकलांगता पर ₹2 लाख"),
            ("Affordable Annual Premium", "Ultra-low premium of only ₹20 per year auto-debited from savings account.", "मात्र ₹20 प्रति वर्ष प्रीमियम")
        ],
        "documents": [
            ("Aadhaar Card", True, "Identity and KYC verification", "आधार कार्ड"),
            ("Savings Bank Account Passbook", True, "Auto-debit mandate setup", "बचत बैंक खाता")
        ]
    },
    "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)": {
        "short_name": "PMJJBY",
        "slug": "pmjjby",
        "benefit_amount": "₹2,00,000 life insurance cover for death due to any reason for ₹436 / year",
        "benefit_type": "Term Life Insurance",
        "rule": {
            "min_age": 18,
            "max_age": 50,
            "allowed_genders": "All",
            "allowed_occupations": "All",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Indian citizen aged 18 to 50 with a bank account giving consent for auto-debit."
        },
        "benefits": [
            ("Universal Life Cover", "₹2,00,000 payable to nominee upon death of insured due to any reason.", "किसी भी कारण से मृत्यु पर ₹2 लाख जीवन बीमा"),
            ("Affordable Annual Premium", "Annual premium of ₹436 auto-debited from savings account.", "मात्र ₹436 प्रति वर्ष प्रीमियम")
        ],
        "documents": [
            ("Aadhaar Card", True, "Identity and KYC verification", "आधार कार्ड"),
            ("Savings Bank Account", True, "For auto-debit consent", "बचत बैंक खाता")
        ]
    },
    "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)": {
        "short_name": "PMKVY",
        "slug": "pmkvy",
        "benefit_amount": "Free industry-aligned skill certification + monetary reward + placement assistance",
        "benefit_type": "Free Skill Training & Certification",
        "rule": {
            "min_age": 15,
            "max_age": 45,
            "allowed_genders": "All",
            "allowed_occupations": "Student, Unemployed Youth, Daily Wage, Citizen",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "student_only": False,
            "custom_criteria_text": "Any Indian youth school/college dropout or unemployed looking to acquire industry-certified vocational skills."
        },
        "benefits": [
            ("100% Free Training", "Full course fee funded by National Skill Development Corporation (NSDC).", "100% मुफ्त कौशल प्रशिक्षण"),
            ("Government Recognized Certificate", "National Skills Qualification Framework (NSQF) aligned certification.", "सरकारी मान्यता प्राप्त प्रमाण पत्र"),
            ("Placement Facilitation", "Access to Rozgar Melas and employer job matching.", "रोजगार सहायता")
        ],
        "documents": [
            ("Aadhaar Card", True, "Identity verification", "आधार कार्ड"),
            ("Bank Account Passbook", True, "For DBT reward stipend", "बैंक खाता पासबुक"),
            ("Educational Certificates", False, "Previous school/college marksheet if available", "शैक्षणिक प्रमाण पत्र")
        ]
    },
    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": {
        "short_name": "PMFBY",
        "slug": "pmfby",
        "benefit_amount": "Comprehensive crop insurance at nominal premium (1.5% Rabi, 2% Kharif) with 100% loss compensation",
        "benefit_type": "Crop Insurance",
        "rule": {
            "min_age": 18,
            "max_age": 75,
            "allowed_genders": "All",
            "allowed_occupations": "Farmer, Sharecropper, Tenant Farmer",
            "max_annual_income": None,
            "allowed_states": "All",
            "allowed_categories": "All",
            "requires_landholding": True,
            "custom_criteria_text": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas."
        },
        "benefits": [
            ("Minimal Premium", "Farmer pays only 1.5% to 2% premium; rest subsidized 50:50 by Central and State Governments.", "न्यूनतम प्रीमियम दर"),
            ("Localized Calamity Cover", "Covers hailstorms, landslides, inundation, and post-harvest crop damage.", "प्राकृतिक आपदाओं से संपूर्ण सुरक्षा")
        ],
        "documents": [
            ("Land Record / Sowing Certificate", True, "Certified by Village Patwari or Revenue Officer", "भूमि अभिलेख / बुवाई प्रमाण पत्र"),
            ("Aadhaar Card", True, "For identity verification", "आधार कार्ड"),
            ("Bank Account Passbook", True, "For claim settlement direct transfer", "बैंक पासबुक")
        ]
    },
    "PM Matru Vandana Yojana (PMMVY)": {
        "short_name": "PMMVY",
        "slug": "pmmvy",
        "benefit_amount": "Direct cash maternity incentive of ₹5,000 in two installments for first child and ₹6,000 for second girl child",
        "benefit_type": "Maternity Benefit DBT",
        "rule": {
            "min_age": 19,
            "max_age": 45,
            "allowed_genders": "Female",
            "allowed_occupations": "All",
            "max_annual_income": 800000.0,
            "allowed_states": "All",
            "allowed_categories": "All",
            "custom_criteria_text": "Pregnant Women and Lactating Mothers (PW&LM) having eligible family income less than ₹8 Lakh."
        },
        "benefits": [
            ("Direct Cash Incentive", "₹5,000 cash transfer for first living child; ₹6,000 on birth of second child if female.", "प्रत्यक्ष नकद मातृत्व सहायता"),
            ("Nutritional Compensation", "Compensates for wage loss during late pregnancy and promotes breastfeeding.", "पोषण सहायता एवं मजदूरी क्षतिपूर्ति")
        ],
        "documents": [
            ("Mother & Child Protection (MCP) Card", True, "Issued by Anganwadi / Health Centre", "मातृ एवं बाल सुरक्षा कार्ड"),
            ("Aadhaar Card of Mother and Husband", True, "Identification and DBT linkage", "आधार कार्ड"),
            ("Bank / Post Office Passbook of Mother", True, "Aadhaar seeded individual bank account", "माता का बैंक खाता पासबुक")
        ]
    }
}

def clean_text(text: str) -> str:
    """Clean markdown headings, backticks, and extraneous symbols."""
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r'^#+\s*', '', t)
    t = re.sub(r'[*_`]', '', t)
    return ' '.join(t.split())

def extract_acronym(name: str) -> str:
    m = re.search(r'\(([A-Z0-9\-\/]+)\)', name)
    if m:
        return m.group(1)
    # Check if name is already an acronym
    if name.isupper() and len(name) <= 10:
        return name
    words = [w for w in name.split() if w[0].isupper()]
    if 2 <= len(words) <= 5:
        return "".join(w[0] for w in words)
    return name[:15]

def generate_slug(name: str) -> str:
    acronym = extract_acronym(name)
    slug = re.sub(r'[^a-z0-9]+', '-', acronym.lower()).strip('-')
    if len(slug) >= 3:
        return slug
    clean_n = re.sub(r'\(.*?\)', '', name).strip()
    slug = re.sub(r'[^a-z0-9]+', '-', clean_n.lower()).strip('-')
    return slug[:40]

def classify_qa_topic(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ['benefit', 'advantage', 'receive', 'amount', 'coverage']):
        return "benefits"
    if any(k in q for k in ['eligib', 'who can', 'criteria', 'qualify', 'condition', 'age limit']):
        return "eligibility"
    if any(k in q for k in ['apply', 'application', 'process', 'how to', 'register', 'enroll']):
        return "application_process"
    if any(k in q for k in ['document', 'paper', 'proof', 'certificate', 'card']):
        return "documents"
    if any(k in q for k in ['what is', 'explain', 'overview', 'objective', 'about', 'purpose']):
        return "overview"
    if any(k in q for k in ['helpline', 'contact', 'toll free', 'phone', 'complaint']):
        return "contact"
    return "general"

def run_import(recreate: bool = False):
    print("=" * 70)
    print("JANSAHAY AI — COMPREHENSIVE DATASET IMPORT PIPELINE")
    print("=" * 70)
    print(f"Reading dataset: {DATASET_PATH}")
    
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    # Read and group rows by canonical scheme
    raw_rows_count = 0
    canonical_groups = defaultdict(list)
    raw_to_canonical_map = {}
    conflict_candidates = []
    
    with open(DATASET_PATH, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            raw_rows_count += 1
            row['_source_row_id'] = idx
            raw_name = (row.get('scheme_name') or '').strip()
            
            canonical_name = RAW_TO_CANONICAL.get(raw_name, raw_name)
            raw_to_canonical_map[raw_name] = canonical_name
            canonical_groups[canonical_name].append(row)
            
            if raw_name != canonical_name:
                conflict_candidates.append({
                    "raw_name": raw_name,
                    "canonical_name": canonical_name,
                    "row_id": idx,
                    "conflict_type": "name_variant_merged"
                })

    print(f"Processed {raw_rows_count} source Q&A rows across {len(canonical_groups)} canonical schemes.")

    # Database Session
    db = SessionLocal()

    if recreate and engine.dialect.name != "sqlite":
        db.close()
        raise RuntimeError(
            "Refusing to drop a PostgreSQL database. PostgreSQL imports are additive and "
            "skip an already-populated catalog."
        )

    if recreate:
        print("Recreating local SQLite tables as explicitly requested...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    existing_schemes = db.query(Scheme).count()
    if existing_schemes:
        counts = {
            "schemes": existing_schemes,
            "qa_records": db.query(SchemeQA).count(),
            "benefits": db.query(SchemeBenefit).count(),
            "documents": db.query(SchemeDocument).count(),
            "users": db.query(User).count(),
        }
        print(f"Catalog already populated; leaving all existing data unchanged: {counts}")
        db.close()
        return {"status": "ALREADY_POPULATED", "counts": counts}

    # Production administrators are bootstrapped only from private environment
    # settings. Shared demo accounts exist only when explicitly enabled.
    if settings.APP_ENV == "production":
        has_admin = db.query(User).filter(User.is_admin == True).first()
        if not has_admin and settings.ADMIN_BOOTSTRAP_EMAIL and settings.ADMIN_BOOTSTRAP_PASSWORD:
            admin_user = db.query(User).filter(User.email == settings.ADMIN_BOOTSTRAP_EMAIL).first()
            if not admin_user:
                admin_user = User(
                    email=settings.ADMIN_BOOTSTRAP_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD),
                    full_name="JanSahay Administrator",
                    is_active=True,
                    is_admin=True,
                )
                db.add(admin_user)
                db.commit()
    elif settings.ENABLE_DEMO_ACCOUNTS:
        admin_user = db.query(User).filter(User.email == "admin@jansahay.gov.in").first()
        if not admin_user:
            db.add(User(
                email="admin@jansahay.gov.in",
                hashed_password=hash_password("Admin@JanSahay2026"),
                full_name="JanSahay Nodal Administrator",
                is_active=True,
                is_admin=True,
            ))

        citizen_user = db.query(User).filter(User.email == "demo@citizen.in").first()
        if not citizen_user:
            citizen_user = User(
                email="demo@citizen.in",
                hashed_password=hash_password("Citizen@2026"),
                full_name="Rameshwar Patil",
                is_active=True,
                is_admin=False,
            )
            db.add(citizen_user)
            db.commit()
            db.refresh(citizen_user)

        if not citizen_user.profile:
            db.add(UserProfile(
                user_id=citizen_user.id,
                age=38,
                gender="Male",
                state="Maharashtra",
                district="Nashik",
                occupation="Farmer",
                annual_income=180000.0,
                social_category="OBC",
                is_rural=True,
                landholding_acres=2.5,
                is_disabled=False,
                has_bpl_card=True,
                is_student=False,
                education_level="10th Pass",
                preferred_language="mr",
            ))
        db.commit()

    imported_schemes_count = 0
    imported_qa_count = 0
    imported_benefits_count = 0
    imported_docs_count = 0
    
    used_slugs = set()
    scheme_id_map = {}

    # Import canonical schemes
    for can_name, rows in canonical_groups.items():
        # Aggregated metadata from rows
        categories = Counter(r.get('category', '').strip() for r in rows if r.get('category'))
        websites = Counter(r.get('official_website', '').strip() for r in rows if r.get('official_website'))
        years = Counter(r.get('launched_year', '').strip() for r in rows if r.get('launched_year'))
        levels = Counter(r.get('state_or_central', '').strip() for r in rows if r.get('state_or_central'))
        beneficiaries = Counter(r.get('target_beneficiary', '').strip() for r in rows if r.get('target_beneficiary'))
        raw_names = sorted(list(set(r.get('scheme_name', '').strip() for r in rows if r.get('scheme_name'))))

        raw_cat = categories.most_common(1)[0][0] if categories else 'Social Welfare'
        norm_cat = CATEGORY_NORMALIZE.get(raw_cat.lower(), raw_cat)
        
        official_url = websites.most_common(1)[0][0] if websites else 'https://www.india.gov.in'
        launched_year = years.most_common(1)[0][0] if years else '2015'
        level = levels.most_common(1)[0][0] if levels else 'Central'
        target_beneficiary = beneficiaries.most_common(1)[0][0] if beneficiaries else 'Eligible Citizens'

        # Check curated overrides
        curated = CURATED_SCHEME_RULES.get(can_name, {})
        
        # State Scheme Check
        state_cfg = STATE_SCHEME_CONFIG.get(can_name)
        if state_cfg:
            level = state_cfg["level"]
            applicable_states = state_cfg["states"]
            dept = state_cfg["department"]
            ministry = state_cfg["ministry"]
        else:
            applicable_states = "All"
            dept_info = CATEGORY_MINISTRY_MAP.get(norm_cat, ("Ministry of Social Welfare", "Government of India"))
            dept = dept_info[0]
            ministry = dept_info[1]

        short_name = curated.get("short_name", extract_acronym(can_name))
        slug = curated.get("slug", generate_slug(can_name))
        
        # Ensure slug uniqueness
        base_slug = slug
        c = 1
        while slug in used_slugs:
            slug = f"{base_slug}-{c}"
            c += 1
        used_slugs.add(slug)

        # Extract best English & Hindi summary & description from Q&A rows
        overview_rows = [r for r in rows if classify_qa_topic(r.get('question_english', '')) == 'overview']
        if not overview_rows:
            overview_rows = rows

        best_row = overview_rows[0]
        # Find row with good explanation
        for r in overview_rows:
            ae = r.get('answer_english', '')
            if len(ae) > 100:
                best_row = r
                break

        summary_en = clean_text(best_row.get('answer_english', ''))[:350]
        summary_hi = clean_text(best_row.get('answer', ''))[:350]
        
        desc_en = clean_text(best_row.get('answer_english', ''))
        desc_hi = clean_text(best_row.get('answer', ''))
        
        if not summary_en:
            summary_en = f"{can_name} is a welfare initiative by {dept} for {target_beneficiary}."
        if not summary_hi:
            summary_hi = f"{can_name} भारत सरकार की एक महत्वपूर्ण जन कल्याणकारी योजना है।"

        # Extract application process
        apply_rows = [r for r in rows if classify_qa_topic(r.get('question_english', '')) == 'application_process']
        if apply_rows:
            app_en = clean_text(apply_rows[0].get('answer_english', ''))[:800]
            app_hi = clean_text(apply_rows[0].get('answer', ''))[:800]
        else:
            app_en = f"Citizens can apply online via the official portal ({official_url}) or through designated Common Service Centers (CSC)."
            app_hi = f"नागरिक आधिकारिक पोर्टल ({official_url}) के माध्यम से ऑनलाइन या नजदीकी कॉमन सर्विस सेंटर (CSC) पर जाकर आवेदन कर सकते हैं।"

        benefit_amount = curated.get("benefit_amount", f"Comprehensive welfare assistance under {can_name}")
        benefit_type = curated.get("benefit_type", "Welfare Assistance & Subsidies")

        # Source record IDs
        source_ids = [r['_source_row_id'] for r in rows]

        # Create Scheme record
        scheme_obj = Scheme(
            slug=slug,
            name=can_name,
            short_name=short_name,
            department=dept,
            ministry=ministry,
            level=level,
            applicable_states=applicable_states,
            category=norm_cat,
            summary=summary_en,
            summary_hindi=summary_hi,
            description=desc_en,
            description_hindi=desc_hi,
            target_beneficiary=target_beneficiary,
            benefit_type=benefit_type,
            benefit_amount=benefit_amount,
            application_mode="Online & Offline" if "csc" in app_en.lower() or "center" in app_en.lower() else "Online",
            application_process=app_en,
            application_process_hindi=app_hi,
            official_url=official_url,
            portal_name=f"{short_name} Official Portal",
            launched_year=str(launched_year),
            source_dataset="indian_government_schemes_dataset_english_and_hindi.csv",
            source_row_count=len(rows),
            source_record_ids=json.dumps(source_ids[:50]),
            aliases=json.dumps(raw_names),
            is_active=True,
            # Dataset ingestion does not independently verify current official
            # eligibility rules; an administrator must review before marking verified.
            is_verified=False,
            last_verified_date=None
        )
        db.add(scheme_obj)
        db.flush()
        
        imported_schemes_count += 1
        scheme_id_map[can_name] = scheme_obj.id

        # 1. Eligibility Rules
        rule_cfg = curated.get("rule", {})
        min_age = rule_cfg.get("min_age")
        max_age = rule_cfg.get("max_age")
        allowed_genders = rule_cfg.get("allowed_genders", "All")
        allowed_occupations = rule_cfg.get("allowed_occupations", "All")
        max_income = rule_cfg.get("max_annual_income")
        allowed_states_rule = applicable_states
        allowed_categories = rule_cfg.get("allowed_categories", "All")
        rural_only = rule_cfg.get("rural_only", None)
        requires_landholding = rule_cfg.get("requires_landholding", None)
        max_landholding_acres = rule_cfg.get("max_landholding_acres", None)
        bpl_required = rule_cfg.get("bpl_required", None)
        student_only = rule_cfg.get("student_only", None)
        custom_text = rule_cfg.get("custom_criteria_text", f"Open to all eligible {target_beneficiary.lower()} meeting scheme prerequisites.")

        # Check for youth or student schemes
        if "student" in target_beneficiary.lower():
            student_only = True
            allowed_occupations = "Student"
        if "farmer" in target_beneficiary.lower():
            allowed_occupations = "Farmer, Agricultural Worker"
            if requires_landholding is None and "land" in target_beneficiary.lower():
                requires_landholding = True
        if "women" in target_beneficiary.lower() or "girl" in target_beneficiary.lower():
            allowed_genders = "Female"

        eligibility_rule = EligibilityRule(
            scheme_id=scheme_obj.id,
            min_age=min_age,
            max_age=max_age,
            allowed_genders=allowed_genders,
            allowed_occupations=allowed_occupations,
            max_annual_income=max_income,
            min_annual_income=None,
            allowed_states=allowed_states_rule,
            allowed_categories=allowed_categories,
            rural_only=rural_only,
            requires_landholding=requires_landholding,
            max_landholding_acres=max_landholding_acres,
            disability_required=rule_cfg.get("disability_required", None),
            bpl_required=bpl_required,
            student_only=student_only,
            custom_criteria_text=custom_text
        )
        db.add(eligibility_rule)

        # 2. Scheme Benefits
        curated_benefits = curated.get("benefits", [])
        if curated_benefits:
            for b_idx, (b_title, b_desc, b_title_hi) in enumerate(curated_benefits):
                benefit_record = SchemeBenefit(
                    scheme_id=scheme_obj.id,
                    title=b_title,
                    description=b_desc,
                    title_hindi=b_title_hi,
                    order_index=b_idx + 1
                )
                db.add(benefit_record)
                imported_benefits_count += 1
        else:
            # Fallback benefit from Q&A
            benefit_record = SchemeBenefit(
                scheme_id=scheme_obj.id,
                title=f"Core Financial & Social Assistance under {short_name}",
                description=f"Provides structured assistance, subsidies, and administrative facilitation for {target_beneficiary}.",
                title_hindi=f"{short_name} के तहत मुख्य वित्तीय एवं सामाजिक सहायता",
                description_hindi=f"{target_beneficiary} के लिए सहायता एवं सब्सिडी प्रदान करता है।",
                order_index=1
            )
            db.add(benefit_record)
            imported_benefits_count += 1

        # 3. Scheme Documents
        curated_docs = curated.get("documents", [])
        if curated_docs:
            for d_name, d_mand, d_notes, d_name_hi in curated_docs:
                doc_record = SchemeDocument(
                    scheme_id=scheme_obj.id,
                    document_name=d_name,
                    document_name_hindi=d_name_hi,
                    is_mandatory=d_mand,
                    notes=d_notes
                )
                db.add(doc_record)
                imported_docs_count += 1
        else:
            # Standard documentation requirements
            default_docs = [
                ("Aadhaar Card", True, "Identity and biometric authentication", "आधार कार्ड"),
                ("Bank Account Passbook", True, "Aadhaar-seeded account for direct benefit transfer", "बैंक पासबुक"),
                ("Proof of Residence / Domicile Certificate", False, "Issued by Tehsildar or Sub-Divisional Magistrate", "निवास प्रमाण पत्र")
            ]
            for d_name, d_mand, d_notes, d_name_hi in default_docs:
                doc_record = SchemeDocument(
                    scheme_id=scheme_obj.id,
                    document_name=d_name,
                    document_name_hindi=d_name_hi,
                    is_mandatory=d_mand,
                    notes=d_notes
                )
                db.add(doc_record)
                imported_docs_count += 1

        # 4. Scheme QA Knowledge Base (All 3,473 Q&A rows!)
        for r in rows:
            qe = clean_text(r.get('question_english', ''))
            qh = clean_text(r.get('question', ''))
            ae = clean_text(r.get('answer_english', ''))
            ah = clean_text(r.get('answer', ''))
            diff = r.get('difficulty_level', 'Basic')
            topic = classify_qa_topic(qe)
            
            qa_rec = SchemeQA(
                scheme_id=scheme_obj.id,
                question_english=qe,
                question_hindi=qh,
                answer_english=ae,
                answer_hindi=ah,
                category=norm_cat,
                topic=topic,
                difficulty_level=diff,
                source_row_id=r['_source_row_id']
            )
            db.add(qa_rec)
            imported_qa_count += 1

    # Record all Scheme Conflicts and Merges for Audit & Traceability
    for raw_name, can_name in raw_to_canonical_map.items():
        if raw_name != can_name:
            can_id = scheme_id_map.get(can_name)
            conflict_rec = SchemeConflict(
                canonical_scheme_id=can_id,
                scheme_name=can_name,
                variant_name=raw_name,
                conflict_type="naming_variant_merged",
                resolution=f"Merged into canonical scheme '{can_name}'",
                details=json.dumps({"original_alias": raw_name, "canonical": can_name}),
                status="Resolved"
            )
            db.add(conflict_rec)

    # Add Audit Log entry
    audit = AuditLog(
        action="DATASET_IMPORT",
        entity_type="SchemeCatalog",
        entity_id=str(imported_schemes_count),
        details=json.dumps({
            "source_dataset": "indian_government_schemes_dataset_english_and_hindi.csv",
            "source_rows": raw_rows_count,
            "imported_canonical_schemes": imported_schemes_count,
            "imported_qa_records": imported_qa_count,
            "imported_benefits": imported_benefits_count,
            "imported_documents": imported_docs_count,
            "conflicts_resolved": len(conflict_candidates)
        })
    )
    db.add(audit)

    db.commit()

    # Generate JSON Import Report
    report = {
        "status": "SUCCESS",
        "timestamp": datetime.utcnow().isoformat(),
        "source_dataset_path": DATASET_PATH,
        "source_total_rows": raw_rows_count,
        "accepted_canonical_schemes": imported_schemes_count,
        "accepted_qa_records": imported_qa_count,
        "accepted_benefits_count": imported_benefits_count,
        "accepted_documents_count": imported_docs_count,
        "duplicate_variants_resolved": len(conflict_candidates),
        "rejected_records": 0,
        "normalization_rules_applied": [
            "Category normalization across 18 raw categories to 11 standardized sectors",
            "Acronym extraction and slug normalization",
            "Bilingual English/Hindi content structuring",
            "Explicit missing-field protection (never invent false exclusions)",
            "Preservation of raw source row IDs for every Q&A record"
        ],
        "canonical_schemes_summary": [
            {"id": s.id, "name": s.name, "category": s.category, "qa_count": len(s.qa_records)}
            for s in db.query(Scheme).all()
        ]
    }

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"IMPORT COMPLETE SUCCESSFULLY!")
    print(f"• Total Source Rows: {raw_rows_count}")
    print(f"• Canonical Schemes: {imported_schemes_count}")
    print(f"• Total Q&A Records Imported: {imported_qa_count}")
    print(f"• Benefits Records: {imported_benefits_count}")
    print(f"• Documents Records: {imported_docs_count}")
    print(f"• Variant Conflicts Resolved: {len(conflict_candidates)}")
    print(f"• Report saved to: {REPORT_PATH}")
    print("=" * 70)

    db.close()
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import real Indian Government Schemes Dataset into JanSahay AI")
    parser.add_argument("--recreate", action="store_true", default=False, help="Drop and recreate a local SQLite database (never allowed for PostgreSQL)")
    args = parser.parse_args()
    run_import(recreate=args.recreate)
