"""
Manual test script to verify CheckSession insert and __repr__ output.
Not intended for automated pytest runs.
"""

import sys
from pathlib import Path

# Add project root to sys.path to allow importing from src
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.db.database import SessionLocal, engine, Base
from src.db.models import CheckSession

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

# Open DB session
session = SessionLocal()

# Create a test CheckSession entry
check = CheckSession(
    filename="demo_file.csv",
    file_format="csv",
    rows=120,
    issues_found=3
)

session.add(check)
session.commit()

# Output should be: <CheckSession(filename=demo_file.csv, issues=3)>
print(check)

# Close session
session.close()