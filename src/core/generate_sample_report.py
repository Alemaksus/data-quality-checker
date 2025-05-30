import pandas as pd
from pathlib import Path
from typing import Optional
from src.core.reporting import generate_markdown_report
from src.core.export_utils import save_markdown, save_html, save_pdf


def generate_data_quality_report(
    input_path: Path,
    report_format: str = "pdf",
    include_ai: bool = True,
    client_name: Optional[str] = None
) -> dict:
    """
    Generates a data quality report from a CSV/JSON file and exports it.

    Args:
        input_path (Path): Path to the dataset file (.csv or .json)
        report_format (str): Output format: "md", "html", "pdf", or "all"
        include_ai (bool): Whether to include AI-based insights
        client_name (str, optional): Optional client name for the report

    Returns:
        dict: Paths to generated report files
    """
    # Load the dataset
    if input_path.suffix == ".csv":
        df = pd.read_csv(input_path)
    elif input_path.suffix == ".json":
        df = pd.read_json(input_path)
    else:
        raise ValueError("Unsupported file format. Only CSV and JSON are supported.")

    # Detect issues (basic stub for now)
    issues = []
    if df.isnull().values.any():
        issues.append("Dataset contains missing values.")

    # Example AI insights
    ai_insights = (
        "Missing values detected. Consider imputation or data cleanup.\n"
        "Check if categorical columns need normalization or encoding."
        if include_ai else ""
    )

    # Generate report
    markdown = generate_markdown_report(df, issues, ai_insights, client_name)

    filename = input_path.stem
    output_paths = {}

    if report_format in ("md", "all"):
        output_paths["markdown"] = save_markdown(markdown, filename)
    if report_format in ("html", "all"):
        output_paths["html"] = save_html(markdown, filename)
    if report_format in ("pdf", "all"):
        output_paths["pdf"] = save_pdf(markdown, filename)

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
