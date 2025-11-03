"""
Creates SQL VIEW `check_summary_view` that combines check_sessions and aggregated issue data.
"""

import sqlite3
import os

# Get absolute path to the database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db', 'db.sqlite3'))

# SQL to create the view
create_view_sql = """
CREATE VIEW IF NOT EXISTS check_summary_view AS
SELECT
    cs.id AS session_id,
    cs.filename,
    cs.file_format,
    cs.created_at,
    COUNT(i.id) AS issue_count,
    SUM(CASE WHEN i.severity = 'high' THEN 1 ELSE 0 END) AS high_severity_issues
FROM check_sessions cs
LEFT JOIN issues i ON cs.id = i.session_id
GROUP BY cs.id
ORDER BY cs.created_at DESC;
"""

# Execute the SQL
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(create_view_sql)
conn.commit()
conn.close()

print("SQL VIEW 'check_summary_view' created successfully.")
