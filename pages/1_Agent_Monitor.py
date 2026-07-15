"""
pages/1_🧭_Agent_Monitor.py — the "Processing" screen. Runs the
pipeline (live or demo) and shows a live checklist + progress bar.
See app.py's docstring for the run_pipeline() integration contract.
"""

import time

import streamlit as st

from ui.components import (
    PIPELINE_STEPS,
    inject_css,
    render_sidebar,
    render_agent_status_list,
    render_page_header,
    render_progress_bar,
)
from ui.history_storage import save_history_entry

try:
    from graph.workflow import run_pipeline

    LIVE_MODE = True
except ImportError:
    LIVE_MODE = False


def _demo_run_pipeline(document_text: str, use_rag: bool):
    """Canned output so this page is fully clickable before
    graph/workflow.py exists. Replace by exporting run_pipeline there."""
    time.sleep(0.5)
    yield "planner", {
        "subtopics": [
            "Overall structure and purpose of the document",
            "Main arguments and supporting evidence",
            "Terminology and key concepts used",
            "Gaps or unsupported claims",
        ]
    }
    time.sleep(0.6)
    sources = [
        {"title": "Related published work on this subject", "url": "https://example.org/related-work", "source_type": "web"},
        {"title": "Internal knowledge base note", "url": "kb://curated/notes-1", "source_type": "rag"},
        {"title": "Background reference article", "url": "https://example.com/background", "source_type": "web"},
    ] if use_rag else [
        {"title": "Related published work on this subject", "url": "https://example.org/related-work", "source_type": "web"},
        {"title": "Background reference article", "url": "https://example.com/background", "source_type": "web"},
    ]
    yield "research", {"sources": sources}
    time.sleep(0.6)
    verified = [{**s, "trust_score": 90 - i * 12, "status": "verified" if i != 1 else "conflict"} for i, s in enumerate(sources)]
    yield "verification", {
        "verified_sources": verified,
        "conflicts": ["One supporting source partially disagrees with a claim in the document."],
    }
    time.sleep(0.6)
    yield "analysis", {
        "trends": ["The document's core claims align with recent published work."],
        "risks": ["Some sections lack citations for specific figures."],
        "insights": ["The strongest section is the methodology; the weakest is the conclusion."],
        "recommendations": ["Cross-check the unsupported figures against a primary source."],
    }
    time.sleep(0.6)
    yield "writer", {
        "executive_summary": (
            "This is placeholder text generated in demo mode — connect graph/workflow.py "
            "to replace it with the Writer Agent's real output.\n\n"
            "It would normally summarize the uploaded document in a few paragraphs, "
            "synthesizing the Planner's subtopics with the Analysis Agent's findings."
        ),
        "key_findings": [
            "The document presents a clear central argument.",
            "Supporting evidence is uneven across sections.",
        ],
        "important_concepts": ["Concept A", "Concept B", "Concept C"],
        "strengths": ["Clear structure", "Well-defined scope"],
        "weaknesses": ["Some claims lack citations", "Conclusion is underdeveloped"],
        "recommendations": ["Add sources for key statistics", "Expand the conclusion section"],
    }
    time.sleep(0.5)
    yield "critic", {"score": 7.8, "feedback": "Demo critic feedback — replace with the real Critic Agent's review."}


st.set_page_config(page_title="AgentHive · Agent Monitor", page_icon="◆", layout="wide")
inject_css()
render_sidebar("Agent Monitor")
render_page_header(
    "Multi-Agent Research Intelligence Platform",
    "Agent Monitor",
    "Live status as each agent processes your document.",
)
st.caption("🟢 Connected to graph/workflow.py" if LIVE_MODE else "🟡 Demo mode — connect graph/workflow.py for real output")

if not st.session_state.get("document_text"):
    st.info("No document yet — upload one on the Home page first.")
    st.page_link("app.py", label="← Go to Home", icon="🏠")
    st.stop()

if "results" not in st.session_state:
    st.session_state.results = {}
if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False


def _draw(states: dict):
    done_count = sum(1 for s in states.values() if s == "done")
    render_progress_bar(done_count, len(PIPELINE_STEPS))
    render_agent_status_list(states)


placeholder = st.empty()
base_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
for k in st.session_state.results:
    base_states[k] = "done"

with placeholder.container():
    _draw(base_states)

if not st.session_state.pipeline_done:
    start_time = time.time()
    pipeline_fn = run_pipeline if LIVE_MODE else _demo_run_pipeline
    for step_key, payload in pipeline_fn(st.session_state.document_text, st.session_state.get("use_rag", True)):
        st.session_state.results[step_key] = payload
        live_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
        for k in st.session_state.results:
            live_states[k] = "done"
        remaining = [k for k, _, _ in PIPELINE_STEPS if k not in st.session_state.results]
        if remaining:
            live_states[remaining[0]] = "running"
        with placeholder.container():
            _draw(live_states)
    st.session_state.elapsed = time.time() - start_time
    st.session_state.pipeline_done = True

    # ── Save this completed run to persistent search history ──────────
    # Stores the full results dict (planner/research/verification/
    # analysis/writer/critic — scores, sources, report, everything) so
    # the sidebar's "Recent Runs" list can reload it later.
    try:
        save_history_entry(
            document_name=st.session_state.document_name,
            results=st.session_state.results,
            elapsed=st.session_state.elapsed,
            use_rag=st.session_state.get("use_rag"),
        )
    except Exception as e:
        st.warning(f"Couldn't save this run to history: {e}")

    st.rerun()
else:
    st.success("Analysis complete.")
    c1, c2 = st.columns(2)
    st.page_link("pages/2_Analysis_Dashboard.py", label="View Analysis Dashboard →", icon="📊", use_container_width=True)
    st.page_link("pages/3_Final_Report.py", label="View Final Report →", icon="📄", use_container_width=True)