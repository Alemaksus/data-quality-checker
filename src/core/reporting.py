import pandas as pd
from datetime import datetime

def generate_markdown_report(df: pd.DataFrame, issues: list[str], ai_insights: str = "") -> str:
    """
    Generate a structured Markdown report with basic statistics, missing values,
    detected issues and AI-generated insights.

    :param df: Input DataFrame
    :param issues: List of textual issues found during validation
    :param ai_insights: Optional AI-generated interpretation of data quality
    :return: Markdown-formatted string
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = []

    report.append(f"# 🧾 Data Quality Report")
    report.append(f"Generated: {now}\n")

    report.append("## 🗂 Dataset Overview")
    report.append(f"- Rows: {df.shape[0]}")
    report.append(f"- Columns: {df.shape[1]}\n")

    report.append("## 📊 Summary Statistics")
    try:
        report.append(df.describe(include='all').to_markdown())
    except Exception as e:
        report.append(f"_Error generating statistics: {e}_")
    report.append("")

    report.append("## 🔎 Missing Values")
    try:
        report.append(df.isnull().sum().to_markdown())
    except Exception as e:
        report.append(f"_Error computing nulls: {e}_")
    report.append("")

    report.append("## ⚠️ Detected Issues")
    if issues:
        for issue in issues:
            report.append(f"- {issue}")
    else:
        report.append("No major data issues detected.")
    report.append("")

    if ai_insights:
        report.append("## 🤖 AI Insights")
        report.append(ai_insights)
        report.append("")

    report.append("## ✅ Recommendations")
    report.append("- Standardize formats (e.g., dates, numeric fields)")
    report.append("- Handle missing values (impute or drop)")
    report.append("- Validate field types and business rules")

    return "\n".join(report)
