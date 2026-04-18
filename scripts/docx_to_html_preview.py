from __future__ import annotations

import base64
import html
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parent.parent
DOCX_PATH = ROOT / "submission" / "Project_Report.docx"
HTML_PATH = ROOT / "submission" / "Project_Report.html"
SCREENSHOTS_DIR = ROOT / "docs" / "screenshots"
DIAGRAMS_DIR = ROOT / "docs" / "diagrams"


def iter_blocks(document: DocumentObject):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def style_to_tag(style_name: str) -> str:
    mapping = {
        "Title": "h1",
        "Heading 1": "h1",
        "Heading 2": "h2",
        "Heading 3": "h3",
    }
    return mapping.get(style_name, "p")


def render_paragraph(paragraph: Paragraph) -> str:
    text = html.escape(paragraph.text.strip())
    if not text:
        return ""

    style_name = paragraph.style.name if paragraph.style else ""
    if style_name == "List Bullet":
        return f"<li>{text}</li>"

    tag = style_to_tag(style_name)
    return f"<{tag}>{text}</{tag}>"


def render_table(table: Table) -> str:
    rows: list[str] = []
    for row_index, row in enumerate(table.rows):
        cells: list[str] = []
        for cell in row.cells:
            value = html.escape(cell.text.strip())
            tag = "th" if row_index == 0 else "td"
            cells.append(f"<{tag}>{value}</{tag}>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return '<table class="doc-table">' + "".join(rows) + "</table>"


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    suffix = path.suffix.lower().lstrip(".") or "png"
    if suffix == "jpg":
        suffix = "jpeg"
    return f"data:image/{suffix};base64,{encoded}"


def render_gallery(title: str, items: list[tuple[str, Path]]) -> str:
    cards: list[str] = []
    for label, path in items:
        if not path.exists():
            continue
        uri = image_data_uri(path)
        cards.append(
            f"""
            <figure class="gallery-card">
              <img src="{uri}" alt="{html.escape(label)}">
              <figcaption>{html.escape(label)}</figcaption>
            </figure>
            """
        )
    if not cards:
        return ""
    return f"""
    <section class="gallery-section">
      <h2>{html.escape(title)}</h2>
      <div class="gallery-grid">
        {''.join(cards)}
      </div>
    </section>
    """


def render_single_image(label: str, path: Path) -> str:
    if not path.exists():
        return ""
    uri = image_data_uri(path)
    return f"""
    <figure class="inline-figure">
      <img src="{uri}" alt="{html.escape(label)}">
      <figcaption>{html.escape(label)}</figcaption>
    </figure>
    """


def build_html() -> str:
    document = Document(DOCX_PATH)
    parts: list[str] = []
    open_list = False
    image_map = {
        "4.1  Introduction": [
            ("Use Case Diagram", DIAGRAMS_DIR / "use_case_diagram.png"),
            ("Architecture Diagram", DIAGRAMS_DIR / "architecture_diagram.png"),
        ],
        "4.2.1 Class diagram": [
            ("Class Diagram", DIAGRAMS_DIR / "class_diagram.png"),
        ],
        "4.3.1 Sequence diagram": [
            ("Sequence Diagram", DIAGRAMS_DIR / "sequence_diagram.png"),
        ],
        "4.3.2 Activity Diagram": [
            ("Activity Diagram", DIAGRAMS_DIR / "activity_diagram.png"),
        ],
        "5.2 Database Entities and Attributes (Schema)": [
            ("Database Diagram", DIAGRAMS_DIR / "database_diagram.png"),
        ],
        "5.4 Interfaces": [
            ("Sign In", SCREENSHOTS_DIR / "01_signin.png"),
            ("Overview", SCREENSHOTS_DIR / "02_overview.png"),
            ("Prediction Result", SCREENSHOTS_DIR / "03_predict_result.png"),
            ("Signals", SCREENSHOTS_DIR / "04_signals.png"),
            ("Dashboard", SCREENSHOTS_DIR / "05_dashboard.png"),
        ],
    }

    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            rendered = render_paragraph(block)
            if not rendered:
                continue
            if rendered.startswith("<li>"):
                if not open_list:
                    parts.append("<ul>")
                    open_list = True
                parts.append(rendered)
            else:
                if open_list:
                    parts.append("</ul>")
                    open_list = False
                parts.append(rendered)
                heading_text = block.text.strip()
                if heading_text in image_map:
                    for label, path in image_map[heading_text]:
                        parts.append(render_single_image(label, path))
        elif isinstance(block, Table):
            if open_list:
                parts.append("</ul>")
                open_list = False
            parts.append(render_table(block))

    if open_list:
        parts.append("</ul>")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Project Report Preview</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --paper: #ffffff;
      --ink: #172033;
      --muted: #5b6475;
      --line: #d7ddea;
      --accent: #2f5ea8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: linear-gradient(180deg, #eef3fb 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: "Georgia", "Times New Roman", serif;
      line-height: 1.65;
    }}
    .page {{
      width: min(960px, calc(100vw - 32px));
      margin: 24px auto;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 40px 52px 64px;
      box-shadow: 0 18px 50px rgba(28, 46, 84, 0.08);
    }}
    .topbar {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
      font-family: Arial, sans-serif;
    }}
    .chip {{
      display: inline-block;
      padding: 8px 12px;
      border-radius: 999px;
      background: #edf3ff;
      color: var(--accent);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }}
    h1, h2, h3 {{
      color: #111827;
      margin-top: 1.4em;
      margin-bottom: 0.45em;
      line-height: 1.25;
    }}
    h1 {{
      font-size: 30px;
      border-bottom: 2px solid #e6ebf5;
      padding-bottom: 10px;
    }}
    h2 {{ font-size: 24px; }}
    h3 {{ font-size: 19px; color: var(--accent); }}
    p, li {{
      font-size: 18px;
      margin: 0 0 12px;
    }}
    ul {{
      margin: 0 0 18px 24px;
      padding: 0;
    }}
    .doc-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0 26px;
      font-size: 16px;
    }}
    .doc-table th, .doc-table td {{
      border: 1px solid var(--line);
      padding: 10px 12px;
      vertical-align: top;
      text-align: left;
    }}
    .doc-table th {{
      background: #f3f6fc;
      font-family: Arial, sans-serif;
      font-weight: 700;
    }}
    .gallery-section {{
      margin: 28px 0 36px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }}
    .gallery-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    .gallery-card {{
      margin: 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fbfcff;
    }}
    .gallery-card img {{
      width: 100%;
      height: auto;
      display: block;
      border-radius: 10px;
      border: 1px solid #e6ebf5;
      background: white;
    }}
    .gallery-card figcaption {{
      margin-top: 10px;
      font-family: Arial, sans-serif;
      font-size: 14px;
      color: var(--muted);
      font-weight: 700;
    }}
    .inline-figure {{
      margin: 16px 0 22px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fbfcff;
    }}
    .inline-figure img {{
      width: 100%;
      height: auto;
      display: block;
      border-radius: 10px;
      border: 1px solid #e6ebf5;
      background: white;
    }}
    .inline-figure figcaption {{
      margin-top: 10px;
      text-align: center;
      font-family: Arial, sans-serif;
      font-size: 14px;
      color: var(--muted);
      font-weight: 700;
    }}
    @media (max-width: 720px) {{
      .page {{
        width: calc(100vw - 20px);
        padding: 24px 18px 40px;
      }}
      p, li {{ font-size: 17px; }}
      .doc-table {{ display: block; overflow-x: auto; }}
      .gallery-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <div class="topbar">
      <a class="chip" href="Project_Report.docx">Download DOCX</a>
    </div>
    {''.join(parts)}
  </main>
</body>
</html>
"""


def main() -> None:
    HTML_PATH.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {HTML_PATH}")


if __name__ == "__main__":
    main()
