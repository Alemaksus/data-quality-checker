import pandas as pd
from reporting import generate_markdown_report
from export_utils import save_markdown, save_html, save_pdf


def main():
    # Step 1: Prepare a sample dataset with common data quality issues
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],  # Missing name in row 4
        "email": [
            "alice@example.com",
            None,
            "charlie@example.com",
            "david@example.com",
            "eve@example.com"
        ],  # Missing email in row 2
        "age": [30, 27, "not_a_number", 45, None]  # Invalid and missing ages
    }
    df = pd.DataFrame(data)

    # Step 2: List manually identified data quality issues
    issues = [
        "Row 3: 'age' is not a number",
        "Row 4: 'name' is missing"
    ]

    # Step 3: Add AI-generated insights (manually inserted here for now)
    ai_insights = (
        "The 'email' field contains 20% missing values. "
        "Consider applying a format validator.\n"
        "'age' should be normalized and strictly numeric. "
        "Missing values may require imputation or filtering."
    )

    # Step 4: Generate a Markdown-formatted report from data and issues
    report = generate_markdown_report(df, issues, ai_insights)

    # Step 5: Save the report in three formats (Markdown, HTML, and PDF)
    filename = "sample_report"
    save_markdown(report, filename)
    save_html(report, filename)
    save_pdf(report, filename)

    print("✅ Sample report successfully saved in the 'reports/' directory.")


if __name__ == "__main__":
    main()
