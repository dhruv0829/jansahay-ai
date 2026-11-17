import csv
import re
import os
import sys
import json
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
csv_path = r'C:\Users\Dhruv\.gemini\antigravity\scratch\jansahay-ai\data\indian_government_schemes_dataset_english_and_hindi.csv'

# Standard canonical groupings mapping raw name to canonical key
RAW_TO_CANONICAL = {
    # Acronym and naming variants
    "AMRUT Mission": "AMRUT",
    "AMRUT (Atal Mission for Rejuvenation and Urban Transformation)": "AMRUT",
    
    "Atal Pension Yojana": "Atal Pension Yojana",
    "Atal Pension Yojana (APY)": "Atal Pension Yojana",
    
    "Ayushman Bharat (PM-JAY)": "Ayushman Bharat (PM-JAY)",
    "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)": "Ayushman Bharat (PM-JAY)",
    
    "Beti Bachao Beti Padhao": "Beti Bachao Beti Padhao",
    "Beti Bachao Beti Padhao (BBBP)": "Beti Bachao Beti Padhao",
    
    "Digital India": "Digital India",
    "Digital India Programme": "Digital India",
    
    "Jal Jeevan Mission": "Jal Jeevan Mission",
    "Jal Jeevan Mission (JJM)": "Jal Jeevan Mission",
    
    "Jan Dhan Yojana": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    "Pradhan Mantri Jan Dhan Yojana (PMJDY)": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    
    "MGNREGA": "MGNREGA",
    "Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA)": "MGNREGA",
    
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

print("Loaded canonical mapping rules.")
