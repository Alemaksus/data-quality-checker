
import os
import markdown
import pdfkit
from pdfkit.configuration import Configuration

# Compute absolute path to the HTML template
TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "templates", "report_template.html")
)


def render_template(content: str, template_path: str) -> str:
    """Reads an HTML template and injects the Markdown HTML content."""
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{content}}", content)


def save_markdown(report_md: str, filename: str, output_dir: str = "reports") -> str:
    """Saves raw Markdown content to a .md file."""
    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, f"{filename}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    return md_path


def save_html(report_md: str, filename: str, output_dir: str = "reports") -> str:
    """Converts Markdown to styled HTML using the template and saves it."""
    os.makedirs(output_dir, exist_ok=True)
    html_body = markdown.markdown(report_md, extensions=['tables'])
    full_html = render_template(html_body, TEMPLATE_PATH)

    html_path = os.path.join(output_dir, f"{filename}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    return html_path


def save_pdf(report_md: str, filename: str, output_dir: str = "reports") -> str:
    """Converts Markdown to styled HTML and renders it as PDF using wkhtmltopdf."""
    os.makedirs(output_dir, exist_ok=True)
    html_body = markdown.markdown(report_md, extensions=['tables'])
    full_html = render_template(html_body, TEMPLATE_PATH)

    temp_html_path = os.path.join(output_dir, f"{filename}.temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Update this path if wkhtmltopdf is installed elsewhere
    config = Configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdf_path = os.path.join(output_dir, f"{filename}.pdf")
    pdfkit.from_file(temp_html_path, pdf_path, configuration=config)

    os.remove(temp_html_path)
    return pdf_path
