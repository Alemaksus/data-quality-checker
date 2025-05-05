"""
Manual test script to insert issue records into the `issues` table.
"""

import sys
import os
from datetime import datetime

# Ensure src is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.db.database import SessionLocal
from src.db.models import Issue

# Create a new database session
db = SessionLocal()

# Define new issue records
new_issues = [
    Issue(
        session_id=1,
        row_number=15,
        column_name="email",
        issue_type="missing_value",
        description="Email is missing for this row",
        severity="medium",
        detected_at=datetime.utcnow()
    ),
    Issue(
        session_id=1,
        row_number=48,
        column_name="phone",
        issue_type="invalid_format",
        description="Phone number is in an invalid format",
        severity="high",
        detected_at=datetime.utcnow()
    ),
    Issue(
        session_id=2,
        row_number=12,
        column_name="country",
        issue_type="unknown_value",
        description="Country value 'XYZ' is not recognized",
        severity="low",
        detected_at=datetime.utcnow()
    )
]

# Insert records into the database
db.add_all(new_issues)
db.commit()

# Output inserted issues
print("Inserted issues:")
for issue in new_issues:
    print(repr(issue))

# Close the database session
db.close()
