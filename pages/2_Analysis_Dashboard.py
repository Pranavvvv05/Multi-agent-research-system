"""
pages/2_📊_Analysis_Dashboard.py — visual/metrics view: success-metric
cards, the verification trust ledger, retrieved sources, and a chart
of source trust scores. (This is the page that wasn't spelled out in
detail in the brief — built as the "see the numbers" companion to the
Final Report's "read the writeup".)
"""

import streamlit as st

from ui.components import (
    inject_css,
    render_analysis,
    render_metrics,
    render_sidebar,
    render_page_header,
    render_sources,
    render_subtopics,
    render_verification,
)

st.set_page_config(page_title="InsightForge · Analysis Dashboard", page_icon="◆", layout="wide")
inject_css()
render_sidebar("Analysis Dashboard")
render_page_header(
    "Multi-Agent Research Intelligence Platform",
    "Analysis Dashboard",
    "Metrics, verification, and supporting sources behind the final report.",
)

results = st.session_state.get("results", {})
if not results:
    st.info("No analysis yet — upload a document on the Home page first.")
    st.page_link("app.py", label="← Go to Home", icon="🏠")
    st.stop()

verified = results.get("verification", {}).get("verified_sources", [])
relevance = (
    100 * sum(1 for s in verified if s.get("status") == "verified") / len(verified)
    if verified else None
)
render_metrics({
    "relevance": relevance,
    "quality": results.get("critic", {}).get("score"),
    "latency": st.session_state.get("elapsed"),
    "sources": len(verified) or len(results.get("research", {}).get("sources", [])) or None,
})

if verified:
    st.markdown('<div class="if-card-label" style="margin-top:0.5rem;">Trust Score by Source</div>', unsafe_allow_html=True)
    chart_data = {s.get("title", f"Source {i+1}")[:28]: s.get("trust_score", 0) for i, s in enumerate(verified)}
    try:
        import plotly.graph_objects as go

        fig = go.Figure(go.Bar(
            x=list(chart_data.values()), y=list(chart_data.keys()), orientation="h",
            marker_color=["#0d9488" if v >= 70 else "#dc2626" for v in chart_data.values()],
        ))
        fig.update_layout(
            height=max(220, 42 * len(chart_data)), margin=dict(l=0, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], title="Trust score"), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.bar_chart(chart_data)

col_left, col_right = st.columns(2)
with col_left:
    if "planner" in results:
        render_subtopics(results["planner"]["subtopics"])
    if "verification" in results:
        render_verification(results["verification"]["verified_sources"], results["verification"].get("conflicts", []))
with col_right:
    if "research" in results:
        render_sources(results["research"]["sources"])
    if "analysis" in results:
        a = results["analysis"]
        render_analysis(a.get("insights", []), a.get("trends", []), a.get("risks", []), a.get("recommendations", []))

st.page_link("pages/3_📄_Final_Report.py", label="View Final Report →", icon="📄")