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

import re
from io import BytesIO
from xml.sax.saxutils import escape

SECTIONS = [
    ("Key Findings", "key_findings"),
    ("Important Concepts", "important_concepts"),
    ("Strengths", "strengths"),
    ("Weaknesses", "weaknesses"),
    ("Recommendations", "recommendations"),
]


# ── Shared markdown parsing helpers ─────────────────────────────────

def _split_bold(text: str):
    """Splits text on **bold** markers, returning (chunk, is_bold) pairs."""
    parts = re.split(r"(\*\*.*?\*\*)", text)
    result = []
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            result.append((part[2:-2], True))
        else:
            result.append((part, False))
    return result


def _add_docx_markdown(doc, text: str):
    """Parses a markdown string and appends proper Word elements
    (headings, bold runs, bullet/numbered lists) instead of dumping
    raw '#'/'-' characters into one plain paragraph."""
    if not text:
        return

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            level = min(len(heading_match.group(1)) + 1, 4)  # keep below title (level 0)
            heading_text = re.sub(r"\*\*(.*?)\*\*", r"\1", heading_match.group(2)).strip()
            doc.add_heading(heading_text, level=level)
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)", line)
        numbered_match = re.match(r"^\d+[\.\)]\s+(.*)", line)

        if bullet_match:
            p = doc.add_paragraph(style="List Bullet")
            item_text = bullet_match.group(1).strip()
        elif numbered_match:
            p = doc.add_paragraph(style="List Number")
            item_text = numbered_match.group(1).strip()
        else:
            p = doc.add_paragraph()
            item_text = line

        for chunk, is_bold in _split_bold(item_text):
            run = p.add_run(chunk)
            run.bold = is_bold


def _markdown_to_pdf_flowables(text: str, styles):
    """Parses markdown into a list of reportlab flowables (headings,
    bullet/numbered lists, paragraphs) instead of one raw text blob."""
    from reportlab.platypus import ListFlowable, ListItem, Paragraph, Spacer

    if not text:
        return []

    flowables = []
    bullet_buffer = []
    number_buffer = []

    def flush_bullets():
        if bullet_buffer:
            items = [ListItem(Paragraph(t, styles["Normal"])) for t in bullet_buffer]
            flowables.append(ListFlowable(items, bulletType="bullet"))
            flowables.append(Spacer(1, 8))
            bullet_buffer.clear()

    def flush_numbers():
        if number_buffer:
            items = [ListItem(Paragraph(t, styles["Normal"])) for t in number_buffer]
            flowables.append(ListFlowable(items, bulletType="1"))
            flowables.append(Spacer(1, 8))
            number_buffer.clear()

    def to_reportlab_bold(t: str) -> str:
        # reportlab's Paragraph understands basic <b> tags
        return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escape(t).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>"))

    heading_styles = {1: "Heading1", 2: "Heading2", 3: "Heading3", 4: "Heading4"}

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            flush_bullets()
            flush_numbers()
            level = min(len(heading_match.group(1)), 4)
            heading_text = re.sub(r"\*\*(.*?)\*\*", r"\1", heading_match.group(2)).strip()
            flowables.append(Paragraph(escape(heading_text), styles[heading_styles[level]]))
            flowables.append(Spacer(1, 6))
            continue

        bullet_match = re.match(r"^[-*]\s+(.*)", line)
        numbered_match = re.match(r"^\d+[\.\)]\s+(.*)", line)

        if bullet_match:
            flush_numbers()
            bullet_buffer.append(to_reportlab_bold(bullet_match.group(1).strip()))
            continue
        if numbered_match:
            flush_bullets()
            number_buffer.append(to_reportlab_bold(numbered_match.group(1).strip()))
            continue

        flush_bullets()
        flush_numbers()
        flowables.append(Paragraph(to_reportlab_bold(line), styles["Normal"]))
        flowables.append(Spacer(1, 4))

    flush_bullets()
    flush_numbers()
    return flowables


# ── DOCX ─────────────────────────────────────────────────────────────

def generate_docx(report: dict) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_heading(report.get("title", "Research Report"), level=0)

    doc.add_heading("Executive Summary", level=1)
    _add_docx_markdown(doc, report.get("executive_summary", ""))

    for heading, key in SECTIONS:
        items = report.get(key, [])
        if not items:
            continue
        doc.add_heading(heading, level=1)
        for item in items:
            p = doc.add_paragraph(style="List Bullet")
            for chunk, is_bold in _split_bold(item):
                run = p.add_run(chunk)
                run.bold = is_bold

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ── PDF ──────────────────────────────────────────────────────────────

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
    story.extend(_markdown_to_pdf_flowables(report.get("executive_summary", ""), styles))
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