import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime
from src.db.database import SessionLocal
from src.db.models import CheckSession

# Open a new database session
db = SessionLocal()

# Define new session records
new_sessions = [
    CheckSession(
        filename="transactions_may.csv",
        file_format="csv",
        rows=420,
        issues_found=6,
        created_at=datetime.utcnow()
    ),
    CheckSession(
        filename="raw_logs.xml",
        file_format="xml",
        rows=90,
        issues_found=15,
        created_at=datetime.utcnow()
    )
]

# Add the new records to the session
db.add_all(new_sessions)
db.commit()

# Print the inserted records
print("Inserted sessions:")
for s in new_sessions:
    print(repr(s))

# Close the session
db.close()
