import csv
import re
import json
import os
import sys
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
csv_path = r'C:\Users\Dhruv\.gemini\antigravity\scratch\jansahay-ai\data\indian_government_schemes_dataset_english_and_hindi.csv'

schemes = defaultdict(list)
with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
    for idx, row in enumerate(csv.DictReader(f)):
        row['_source_row_id'] = idx
        s_name = (row.get('scheme_name') or '').strip()
        schemes[s_name].append(row)

print(f"Loaded {sum(len(v) for v in schemes.values())} rows across {len(schemes)} raw scheme names.")
