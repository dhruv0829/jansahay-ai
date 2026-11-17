"""
JanSahay AI — Database Seed and Dataset Population Script.
Loads the complete verified Government Schemes catalog (3,473 Q&A records across 73 canonical schemes).
"""
import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.import_dataset import run_import

def seed_database(recreate: bool = False):
    print("Executing JanSahay AI Database Seeding via verified Real Dataset Pipeline...")
    return run_import(recreate=recreate)

if __name__ == "__main__":
    recreate = "--recreate" in sys.argv
    seed_database(recreate=recreate)
