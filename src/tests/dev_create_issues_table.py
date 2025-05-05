"""
Developer utility to create tables in the database if they do not exist.
Currently focuses on check_sessions and issues tables.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.db.database import engine, Base
from src.db import models # noqa: F401  # ensure models are loaded for metadata

# Create tables based on ORM models
Base.metadata.create_all(bind=engine)

print("Tables successfully created (if they were missing).")
