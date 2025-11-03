import pandas as pd
from pathlib import Path
from typing import Optional, Dict
from src.core.reporting import generate_markdown_report
from src.core.export_utils import save_markdown, save_html, save_pdf, save_excel
from src.core.validator import validate_dataframe
from src.core.ml_advisor import get_ml_recommendations
from src.core.visualizations import (
    generate_missing_values_chart,
    generate_missing_percentage_chart,
    generate_issues_severity_chart,
    generate_all_numeric_distributions
)
from src.db.database import SessionLocal, engine, Base
from src.db.models import CheckSession, Issue
from datetime import datetime


def save_check_to_db(
    filename: str,
    file_format: str,
    rows: int,
    validation_issues: list[dict],
    db_session=None
) -> Optional[int]:
    """
    Save validation check results to database.
    
    Args:
        filename: Name of the file that was checked
        file_format: Format of the file (csv, json, etc.)
        rows: Number of rows in the dataset
        validation_issues: List of validation issue dictionaries
        db_session: Optional database session (creates new if None)
        
    Returns:
        Session ID if successful, None otherwise
    """
    session_created = False
    if db_session is None:
        db_session = SessionLocal()
        session_created = True
    
    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)
        
        # Count issues by severity
        high_severity_count = sum(1 for issue in validation_issues if issue.get('severity') == 'high')
        
        # Create CheckSession
        check_session = CheckSession(
            filename=filename,
            file_format=file_format,
            rows=rows,
            issues_found=len(validation_issues),
            created_at=datetime.utcnow()
        )
        
        db_session.add(check_session)
        db_session.flush()  # Get the ID
        
        # Create Issue records
        for issue_dict in validation_issues:
            issue = Issue(
                session_id=check_session.id,
                row_number=issue_dict.get('row_number'),
                column_name=issue_dict.get('column_name'),
                issue_type=issue_dict.get('issue_type'),
                description=issue_dict.get('description'),
                severity=issue_dict.get('severity', 'medium'),
                detected_at=datetime.utcnow()
            )
            db_session.add(issue)
        
        db_session.commit()
        return check_session.id
    
    except Exception as e:
        db_session.rollback()
        print(f"Error saving to database: {e}")
        return None
    
    finally:
        if session_created:
            db_session.close()


def generate_data_quality_report(
    input_path: Path,
    report_format: str = "pdf",
    include_ai: bool = True,
    client_name: Optional[str] = None,
    save_to_db: bool = True
) -> dict:
    """
    Generates a data quality report from a CSV/JSON file and exports it.

    Args:
        input_path (Path): Path to the dataset file (.csv or .json)
        report_format (str): Output format: "md", "html", "pdf", or "all"
        include_ai (bool): Whether to include AI-based insights
        client_name (str, optional): Optional client name for the report
        save_to_db (bool): Whether to save check results to database

    Returns:
        dict: Paths to generated report files and session_id if saved to DB
    """
    # Load the dataset
    if input_path.suffix == ".csv":
        df = pd.read_csv(input_path)
    elif input_path.suffix == ".json":
        df = pd.read_json(input_path)
    else:
        raise ValueError("Unsupported file format. Only CSV and JSON are supported.")

    # Run validation
    validation_issues, validation_summary = validate_dataframe(df)
    
    # Get ML recommendations if requested
    ml_recommendations = None
    ml_insights = ""
    if include_ai:
        ml_recommendations = get_ml_recommendations(df, validation_issues)
        # Format ML recommendations as text
        if ml_recommendations.get('recommendations'):
            ml_insights = f"**ML Readiness Score**: {ml_recommendations['readiness_score']}/100 ({ml_recommendations['readiness_level']})\n\n"
            ml_insights += "**Recommendations for ML Preparation:**\n\n"
            for rec in ml_recommendations['recommendations'][:15]:  # Limit to first 15
                ml_insights += f"- {rec}\n"
    
    # Convert validation issues to readable format for report
    issue_texts = []
    for issue in validation_issues[:50]:  # Limit to first 50 for readability
        desc = issue['description']
        if issue.get('row_number') is not None:
            desc = f"Row {issue['row_number'] + 1}: {desc}"
        issue_texts.append(desc)
    
    # Save to database if requested
    session_id = None
    if save_to_db:
        session_id = save_check_to_db(
            filename=input_path.name,
            file_format=input_path.suffix[1:] if input_path.suffix else "unknown",
            rows=len(df),
            validation_issues=validation_issues
        )

    # Generate report
    markdown = generate_markdown_report(
        df, 
        issue_texts, 
        ml_insights if include_ai else "", 
        client_name
    )

    filename = input_path.stem
    output_paths = {}

    # Generate visualizations for HTML reports
    visualizations = {}
    if report_format in ("html", "all", "xlsx"):
        visualizations["missing_values"] = generate_missing_values_chart(df)
        visualizations["missing_percentage"] = generate_missing_percentage_chart(df)
        visualizations["issues_severity"] = generate_issues_severity_chart(validation_issues)
        visualizations["numeric_distributions"] = generate_all_numeric_distributions(df)

    if report_format in ("md", "all"):
        output_paths["markdown"] = save_markdown(markdown, filename)
    if report_format in ("html", "all"):
        output_paths["html"] = save_html(markdown, filename, visualizations=visualizations)
    if report_format in ("pdf", "all"):
        output_paths["pdf"] = save_pdf(markdown, filename)
    if report_format in ("xlsx", "excel", "all"):
        try:
            output_paths["excel"] = save_excel(
                df=df,
                validation_issues=validation_issues,
                validation_summary=validation_summary,
                ml_recommendations=ml_recommendations,
                filename=filename
            )
        except ImportError:
            output_paths["excel"] = None  # openpyxl not installed
    
    # Add metadata to output
    output_paths["session_id"] = session_id
    output_paths["issues_count"] = len(validation_issues)
    output_paths["validation_summary"] = validation_summary
    if ml_recommendations:
        output_paths["ml_readiness_score"] = ml_recommendations["readiness_score"]
        output_paths["ml_readiness_level"] = ml_recommendations["readiness_level"]

    return output_paths


# Demo entry point for CLI/testing
def main():
    # Sample dataset with quality issues
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],
        "email": [
            "alice@example.com",
            None,
            "charlie@example.com",
            "david@example.com",
            "eve@example.com"
        ],
        "age": [30, 27, "not_a_number", 45, None]
    }
    df = pd.DataFrame(data)

    issues = [
        "Row 3: 'age' is not a number",
        "Row 4: 'name' is missing"
    ]
    ai_insights = (
        "The 'email' field contains 20% missing values. "
        "Consider applying a format validator.\n"
        "'age' should be normalized and strictly numeric."
    )

    markdown = generate_markdown_report(df, issues, ai_insights)

    filename = "sample_report"
    save_markdown(markdown, filename)
    save_html(markdown, filename)
    save_pdf(markdown, filename)

    print("✅ Sample report successfully saved in the 'reports/' directory.")


if __name__ == "__main__":
    main()
