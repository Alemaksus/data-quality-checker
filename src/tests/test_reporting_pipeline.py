import os
import pandas as pd
from src.core.reporting import generate_markdown_report
from src.core.export_utils import save_markdown, save_html, save_pdf


def test_report_generation_pipeline():
    # Создаём тестовый DataFrame
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve"],
        "email": ["alice@example.com", None, "charlie@example.com", "david@example.com", "eve@example.com"],
        "age": [30, 27, "not_a_number", 45, None]
    }
    df = pd.DataFrame(data)

    # Имитация найденных проблем
    issues = ["Row 3: 'age' is not a number", "Row 4: name is missing"]
    ai = "Consider validating the 'email' field and normalizing 'age'."

    # Генерация отчёта
    md = generate_markdown_report(df, issues, ai)

    # Сохраняем отчёты
    filename = "test_report"
    md_path = save_markdown(md, filename)
    html_path = save_html(md, filename)

    # Проверяем, что файлы созданы
    assert os.path.exists(md_path), "Markdown report not created"
    assert os.path.exists(html_path), "HTML report not created"

    # Пробуем сохранить PDF (если wkhtmltopdf установлен)
    try:
        pdf_path = save_pdf(md, filename)
        assert os.path.exists(pdf_path), "PDF report not created"
    except Exception as e:
        print("⚠️ PDF generation skipped:", e)
