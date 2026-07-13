"""
pages/3_📄_Final_Report.py — the polished, downloadable output.
Reads results["writer"] (see app.py's docstring for its exact shape).
"""

import streamlit as st

from ui.components import (
    inject_css,
    render_arrow_list,
    render_concepts,
    render_numbered_list,
    render_sidebar,
    render_page_header,
    render_swot,
    render_text_panel,
)
from ui.report_export import generate_docx, generate_pdf

st.set_page_config(page_title="InsightForge · Final Report", page_icon="◆", layout="wide")
inject_css()
render_sidebar("Final Report")

results = st.session_state.get("results", {})
if "writer" not in results:
    render_page_header("Multi-Agent Research Intelligence Platform", "Final Report")
    st.info("No report yet — upload a document on the Home page first.")
    st.page_link("app.py", label="← Go to Home", icon="🏠")
    st.stop()

writer = results["writer"]
document_name = st.session_state.get("document_name", "document")
render_page_header(
    "Multi-Agent Research Intelligence Platform",
    "Final Report",
    f"Generated from {document_name}",
)

col_main, col_side = st.columns([2.4, 1])

with col_main:
    render_text_panel("Executive Summary", writer.get("executive_summary", ""), "signal")
    render_numbered_list("Key Findings", writer.get("key_findings", []), "signal")
    render_concepts(writer.get("important_concepts", []))
    render_swot(writer.get("strengths", []), writer.get("weaknesses", []))
    render_arrow_list("Recommendations", writer.get("recommendations", []), "insight")

with col_side:
    st.markdown('<div class="if-card-label">Export</div>', unsafe_allow_html=True)

    export_payload = {**writer, "title": document_name}

    export_payload = {**writer, "title": document_name}
    try:
        pdf_bytes = generate_pdf(export_payload)
        st.download_button(
            "⬇ Download PDF", data=pdf_bytes, file_name=f"{document_name}_report.pdf",
            mime="application/pdf", use_container_width=True,
        )
    except ImportError:
        st.caption("Install `reportlab` to enable PDF export.")

    try:
        docx_bytes = generate_docx(export_payload)
        st.download_button(
            "⬇ Download DOCX", data=docx_bytes, file_name=f"{document_name}_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    except ImportError:
        st.caption("Install `python-docx` to enable DOCX export.")

    st.page_link("pages/2_📊_Analysis_Dashboard.py", label="← Back to Analysis Dashboard", icon="📊")