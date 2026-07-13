"""
ui/report_export.py
--------------------
Turns the Writer Agent's structured output into downloadable DOCX and
PDF files. Uses python-docx and reportlab — both pure-Python, so they
work in any deployment (no LibreOffice/pandoc system dependency needed).

Requires: python-docx, reportlab (add to requirements.txt if not present).

Expected `report` dict shape (same as the "writer" pipeline payload,
plus a "title"):
    {
        "title": str,
        "executive_summary": str,
        "key_findings": [str, ...],
        "important_concepts": [str, ...],
        "strengths": [str, ...],
        "weaknesses": [str, ...],
        "recommendations": [str, ...],
    }
"""

from io import BytesIO
from xml.sax.saxutils import escape

SECTIONS = [
    ("Key Findings", "key_findings"),
    ("Important Concepts", "important_concepts"),
    ("Strengths", "strengths"),
    ("Weaknesses", "weaknesses"),
    ("Recommendations", "recommendations"),
]


def generate_docx(report: dict) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_heading(report.get("title", "Research Report"), level=0)

    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph(report.get("executive_summary", ""))

    for heading, key in SECTIONS:
        items = report.get(key, [])
        if not items:
            continue
        doc.add_heading(heading, level=1)
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def generate_pdf(report: dict) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, title=report.get("title", "Research Report"))
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(escape(report.get("title", "Research Report")), styles["Title"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(Paragraph(escape(report.get("executive_summary", "")), styles["Normal"]))
    story.append(Spacer(1, 12))

    for heading, key in SECTIONS:
        items = report.get(key, [])
        if not items:
            continue
        story.append(Paragraph(heading, styles["Heading1"]))
        bullets = [ListItem(Paragraph(escape(item), styles["Normal"])) for item in items]
        story.append(ListFlowable(bullets, bulletType="bullet"))
        story.append(Spacer(1, 12))

    doc.build(story)
    return buf.getvalue()