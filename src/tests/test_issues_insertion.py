import pytest
from src.db.models import Issue

def test_issue_records_exist(db):
    issues = db.query(Issue).all()
    assert len(issues) >= 2, "There should be at least two issue records in the database."

def test_issue_fields_are_not_empty(db):
    issues = db.query(Issue).all()
    for issue in issues:
        assert issue.issue_type, f"Issue ID {issue.id} has an empty issue_type"
        assert issue.column_name, f"Issue ID {issue.id} has an empty column_name"
