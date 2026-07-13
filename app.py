# import streamlit as st

# # --- STEP 1: GLOBAL VIEWPORT SETUP ---
# # Pure framework stack execution ke pehle page layout configure karna zaroori hai.
# st.set_page_config(
#     page_title="InsightForge AI",
#     page_icon="🚀",
#     layout="wide"
# )

# # --- STEP 2: MODULAR SCREEN SUB-IMPORTS ---
# # Hum isolated frontend screen layers ko ui/ subfolder se access kar rahe hain.
# from ui.page_home import render_home
# from ui.page_workspace import render_workspace
# from ui.page_knowledge import render_knowledge_base

# # --- STEP 3: PLATFORM ROUTING DICTIONARY SETUP ---
# # Streamlit ke native Page class routing parameters schema ke mutabik views create karte hain.
# pages = {
#     "Overview & Architecture": [
#         st.Page(render_home, title="Home Dashboard", icon="🏠"),
#     ],
#     "Core Execution Engine": [
#         st.Page(render_workspace, title="Research Workspace", icon="🔍"),
#         st.Page(render_knowledge_base, title="RAG Knowledge Base", icon="📚"),
#     ]
# }

# # --- STEP 4: ACTIVE NAVIGATION BOOTSTRAPPING ---
# # Navigation compilation logic execute karke runtime pipeline ko render space allot karte hain.
# navigation_router = st.navigation(pages)
# navigation_router.run()


# """
# InsightForge — Multi-Agent Research Intelligence Platform
# Frontend entrypoint.
#
# INTEGRATION CONTRACT for whoever wires up graph/workflow.py:
#
#     from graph.workflow import run_pipeline
#
#     def run_pipeline(topic: str, use_rag: bool = True):
#         '''Generator. Yields (step_key, payload) after each agent finishes,
#         in this order: planner -> research -> verification -> analysis
#         -> writer -> critic.'''
#         ...
#         yield "planner", {"subtopics": [...]}
#         yield "research", {"sources": [{"title","url","source_type":"web"|"rag"}, ...]}
#         yield "verification", {
#             "verified_sources": [{"title","url","trust_score":0-100,
#                                    "status":"verified"|"conflict"|"unverified"}, ...],
#             "conflicts": [str, ...],
#         }
#         yield "analysis", {"insights":[...], "trends":[...], "risks":[...], "recommendations":[...]}
#         yield "writer", {"report_markdown": str}
#         yield "critic", {"score": float, "feedback": str, "strengths":[...], "improvements":[...]}
#
# Until graph/workflow.py exports run_pipeline, this file runs in DEMO MODE
# with canned output so the UI stays fully clickable/demoable on its own.
# """

# import time

# import streamlit as st

# from ui.components import (
#     PIPELINE_STEPS,
#     _md,
#     inject_css,
#     render_analysis,
#     render_critic,
#     render_footer,
#     render_header,
#     render_metrics,
#     render_pipeline_chain,
#     render_report,
#     render_sources,
#     render_subtopics,
#     render_verification,
# )

# try:
#     from graph.workflow import run_pipeline  # teammates' real pipeline
#
#     LIVE_MODE = True
# except ImportError:
#     LIVE_MODE = False


# # ── Demo pipeline (used only until graph/workflow.py exists) ────────────────
# def _demo_run_pipeline(topic: str, use_rag: bool):
#     time.sleep(0.5)
#     yield "planner", {
#         "subtopics": [
#             f"Definition and current state of {topic}",
#             f"Key players and recent developments in {topic}",
#             f"Risks, limitations, and open challenges in {topic}",
#             f"Near-term outlook for {topic}",
#         ]
#     }
#     time.sleep(0.6)
#     sources = [
#         {"title": f"{topic}: a 2026 overview", "url": "https://example.org/overview", "source_type": "web"},
#         {"title": f"Recent advances in {topic}", "url": "https://arxiv.org/abs/xxxx.xxxxx", "source_type": "web"},
#         {"title": f"{topic} — internal knowledge base note", "url": "kb://curated/notes-1", "source_type": "rag"},
#         {"title": f"Industry report on {topic}", "url": "https://example.com/report", "source_type": "web"},
#         {"title": f"{topic} dataset documentation", "url": "kb://curated/docs-3", "source_type": "rag"},
#     ] if use_rag else [
#         {"title": f"{topic}: a 2026 overview", "url": "https://example.org/overview", "source_type": "web"},
#         {"title": f"Recent advances in {topic}", "url": "https://arxiv.org/abs/xxxx.xxxxx", "source_type": "web"},
#         {"title": f"Industry report on {topic}", "url": "https://example.com/report", "source_type": "web"},
#     ]
#     yield "research", {"sources": sources}
#     time.sleep(0.6)
#     verified = [
#         {**s, "trust_score": 92, "status": "verified"} if i % 3 != 2 else
#         {**s, "trust_score": 58, "status": "conflict"}
#         for i, s in enumerate(sources)
#     ]
#     yield "verification", {
#         "verified_sources": verified,
#         "conflicts": [f"Two sources disagree on the pace of adoption for {topic}."],
#     }
#     time.sleep(0.6)
#     yield "analysis", {
#         "trends": [f"Growing interest in {topic} across academic and industry venues."],
#         "risks": [f"Data quality and source bias remain open concerns for {topic}."],
#         "insights": [f"Most recent progress in {topic} clusters around the last 12 months."],
#         "recommendations": [f"Track primary sources on {topic} rather than aggregator summaries."],
#     }
#     time.sleep(0.6)
#     yield "writer", {
#         "report_markdown": (
#             f"## {topic}\n\n"
#             f"This is placeholder report text generated in **demo mode** — connect "
#             f"`graph/workflow.py` to replace this with the Writer Agent's real output.\n\n"
#             f"### Summary\nDemo content describing {topic} would appear here, "
#             f"structured with citations back to the sources listed above.\n"
#         )
#     }
#     time.sleep(0.5)
#     yield "critic", {
#         "score": 7.8,
#         "feedback": "Demo critic feedback — replace with the real Critic Agent's review.",
#         "strengths": ["Clear structure", "Sources are cited"],
#         "improvements": ["Add more quantitative detail", "Expand the risk section"],
#     }


# # ── Page setup ────────────────────────────────────────────────────────────
# st.set_page_config(page_title="InsightForge · Research Intelligence", page_icon="◆", layout="wide")
# inject_css()
# render_header()

# # ── Session state ────────────────────────────────────────────────────────
# for key, default in (("results", {}), ("running", False), ("start_time", None), ("elapsed", None)):
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ── Config + run controls ────────────────────────────────────────────────
# col_input, col_config = st.columns([3, 1.3])

# with col_input:
#     _md('<div class="if-card">')
#     _md('<div class="if-card-label">Research Topic</div>')
#     topic = st.text_input(
#         "topic", placeholder="e.g. Multi-agent LLM orchestration frameworks",
#         label_visibility="collapsed", key="topic_input",
#     )
#     run_clicked = st.button("Run Research Pipeline", use_container_width=True)
#     _md("</div>")

# with col_config:
#     _md('<div class="if-card">')
#     _md('<div class="if-card-label">Configuration</div>')
#     use_rag = st.checkbox("Use ChromaDB knowledge base", value=True)
#     st.caption(f"{'🟢 Live pipeline' if LIVE_MODE else '🟡 Demo mode — connect graph/workflow.py'}")
#     _md("</div>")

# _md('<div class="if-rule"></div>')

# # ── Pipeline signal chain ───────────────────────────────────────────────
# step_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
# for k in st.session_state.results:
#     step_states[k] = "done"
# render_pipeline_chain(step_states)

# # ── Trigger run ──────────────────────────────────────────────────────────
# if run_clicked:
#     if not topic.strip():
#         st.warning("Enter a research topic to start the pipeline.")
#     else:
#         st.session_state.results = {}
#         st.session_state.running = True
#         st.session_state.start_time = time.time()
#         st.session_state.elapsed = None
#         st.rerun()

# if st.session_state.running:
#     pipeline_fn = run_pipeline if LIVE_MODE else _demo_run_pipeline
#     placeholder = st.empty()
#     for step_key, payload in pipeline_fn(st.session_state.topic_input, use_rag):
#         st.session_state.results[step_key] = payload
#         with placeholder.container():
#             live_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
#             for k in st.session_state.results:
#                 live_states[k] = "done"
#             remaining = [k for k, _, _ in PIPELINE_STEPS if k not in st.session_state.results]
#             if remaining:
#                 live_states[remaining[0]] = "running"
#             render_pipeline_chain(live_states)
#     st.session_state.elapsed = time.time() - st.session_state.start_time
#     st.session_state.running = False
#     st.rerun()

# # ── Metrics strip ────────────────────────────────────────────────────────
# r = st.session_state.results
# if r:
#     verified = r.get("verification", {}).get("verified_sources", [])
#     relevance = (
#         100 * sum(1 for s in verified if s.get("status") == "verified") / len(verified)
#         if verified else None
#     )
#     render_metrics({
#         "relevance": relevance,
#         "quality": r.get("critic", {}).get("score"),
#         "latency": st.session_state.elapsed,
#         "sources": len(verified) if verified else (len(r.get("research", {}).get("sources", [])) or None),
#     })

# # ── Results ──────────────────────────────────────────────────────────────
# if r:
#     tab_report, tab_sources, tab_analysis, tab_critic = st.tabs(
#         ["Report", "Sources & Verification", "Analysis", "Critic"]
#     )

#     with tab_report:
#         if "planner" in r:
#             render_subtopics(r["planner"]["subtopics"])
#         if "writer" in r:
#             render_report(r["writer"]["report_markdown"])
#             st.download_button(
#                 "⬇ Download report (.md)",
#                 data=r["writer"]["report_markdown"],
#                 file_name=f"insightforge_report_{int(time.time())}.md",
#                 mime="text/markdown",
#             )

#     with tab_sources:
#         if "research" in r:
#             render_sources(r["research"]["sources"])
#         if "verification" in r:
#             render_verification(
#                 r["verification"]["verified_sources"],
#                 r["verification"].get("conflicts", []),
#             )

#     with tab_analysis:
#         if "analysis" in r:
#             a = r["analysis"]
#             render_analysis(
#                 a.get("insights", []), a.get("trends", []),
#                 a.get("risks", []), a.get("recommendations", []),
#             )
#         else:
#             st.info("Analysis will appear once the Analysis Agent completes.")

#     with tab_critic:
#         if "critic" in r:
#             c = r["critic"]
#             render_critic(c["score"], c["feedback"], c.get("strengths", []), c.get("improvements", []))
#         else:
#             st.info("Critic review will appear once the Critic Agent completes.")

# render_footer()


# """
# InsightForge — Multi-Agent Research Intelligence Platform
# Frontend entrypoint.
#
# INTEGRATION CONTRACT for whoever wires up graph/workflow.py:
#
#     from graph.workflow import run_pipeline
#
#     def run_pipeline(topic: str, use_rag: bool = True):
#         '''Generator. Yields (step_key, payload) after each agent finishes,
#         in this order: planner -> research -> verification -> analysis
#         -> writer -> critic.'''
#         ...
#         yield "planner", {"subtopics": [...]}
#         yield "research", {"sources": [{"title","url","source_type":"web"|"rag"}, ...]}
#         yield "verification", {
#             "verified_sources": [{"title","url","trust_score":0-100,
#                                    "status":"verified"|"conflict"|"unverified"}, ...],
#             "conflicts": [str, ...],
#         }
#         yield "analysis", {"insights":[...], "trends":[...], "risks":[...], "recommendations":[...]}
#         yield "writer", {"report_markdown": str}
#         yield "critic", {"score": float, "feedback": str, "strengths":[...], "improvements":[...]}
#
# Until graph/workflow.py exports run_pipeline, this file runs in DEMO MODE
# with canned output so the UI stays fully clickable/demoable on its own.
# """

# import time

# import streamlit as st

# from ui import storage
# from ui.components import (
#     PIPELINE_STEPS,
#     _md,
#     inject_css,
#     render_analysis,
#     render_critic,
#     render_footer,
#     render_header,
#     render_metrics,
#     render_pipeline_chain,
#     render_report,
#     render_sources,
#     render_subtopics,
#     render_verification,
# )

# try:
#     from graph.workflow import run_pipeline  # teammates' real pipeline
#
#     LIVE_MODE = True
# except ImportError:
#     LIVE_MODE = False


# # ── Demo pipeline (used only until graph/workflow.py exists) ────────────────
# def _demo_run_pipeline(topic: str, use_rag: bool):
#     time.sleep(0.5)
#     yield "planner", {
#         "subtopics": [
#             f"Definition and current state of {topic}",
#             f"Key players and recent developments in {topic}",
#             f"Risks, limitations, and open challenges in {topic}",
#             f"Near-term outlook for {topic}",
#         ]
#     }
#     time.sleep(0.6)
#     sources = [
#         {"title": f"{topic}: a 2026 overview", "url": "https://example.org/overview", "source_type": "web"},
#         {"title": f"Recent advances in {topic}", "url": "https://arxiv.org/abs/xxxx.xxxxx", "source_type": "web"},
#         {"title": f"{topic} — internal knowledge base note", "url": "kb://curated/notes-1", "source_type": "rag"},
#         {"title": f"Industry report on {topic}", "url": "https://example.com/report", "source_type": "web"},
#         {"title": f"{topic} dataset documentation", "url": "kb://curated/docs-3", "source_type": "rag"},
#     ] if use_rag else [
#         {"title": f"{topic}: a 2026 overview", "url": "https://example.org/overview", "source_type": "web"},
#         {"title": f"Recent advances in {topic}", "url": "https://arxiv.org/abs/xxxx.xxxxx", "source_type": "web"},
#         {"title": f"Industry report on {topic}", "url": "https://example.com/report", "source_type": "web"},
#     ]
#     yield "research", {"sources": sources}
#     time.sleep(0.6)
#     verified = [
#         {**s, "trust_score": 92, "status": "verified"} if i % 3 != 2 else
#         {**s, "trust_score": 58, "status": "conflict"}
#         for i, s in enumerate(sources)
#     ]
#     yield "verification", {
#         "verified_sources": verified,
#         "conflicts": [f"Two sources disagree on the pace of adoption for {topic}."],
#     }
#     time.sleep(0.6)
#     yield "analysis", {
#         "trends": [f"Growing interest in {topic} across academic and industry venues."],
#         "risks": [f"Data quality and source bias remain open concerns for {topic}."],
#         "insights": [f"Most recent progress in {topic} clusters around the last 12 months."],
#         "recommendations": [f"Track primary sources on {topic} rather than aggregator summaries."],
#     }
#     time.sleep(0.6)
#     yield "writer", {
#         "report_markdown": (
#             f"## {topic}\n\n"
#             f"This is placeholder report text generated in **demo mode** — connect "
#             f"`graph/workflow.py` to replace this with the Writer Agent's real output.\n\n"
#             f"### Summary\nDemo content describing {topic} would appear here, "
#             f"structured with citations back to the sources listed above.\n"
#         )
#     }
#     time.sleep(0.5)
#     yield "critic", {
#         "score": 7.8,
#         "feedback": "Demo critic feedback — replace with the real Critic Agent's review.",
#         "strengths": ["Clear structure", "Sources are cited"],
#         "improvements": ["Add more quantitative detail", "Expand the risk section"],
#     }


# # ── Page setup ────────────────────────────────────────────────────────────
# st.set_page_config(page_title="InsightForge · Research Intelligence", page_icon="◆", layout="wide")
# inject_css()
# render_header()

# # ── Session state ────────────────────────────────────────────────────────
# for key, default in (("results", {}), ("running", False), ("start_time", None), ("elapsed", None)):
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ── Config + run controls ────────────────────────────────────────────────
# col_input, col_config = st.columns([3, 1.3])

# with col_input:
#     _md('<div class="if-card">')
#     _md('<div class="if-card-label">Research Topic</div>')
#     topic = st.text_input(
#         "topic", placeholder="e.g. Multi-agent LLM orchestration frameworks",
#         label_visibility="collapsed", key="topic_input",
#     )
#     run_clicked = st.button("Run Research Pipeline", use_container_width=True)
#     _md("</div>")

# with col_config:
#     _md('<div class="if-card">')
#     _md('<div class="if-card-label">Configuration</div>')
#     use_rag = st.checkbox("Use ChromaDB knowledge base", value=True)
#     st.caption(f"{'🟢 Live pipeline' if LIVE_MODE else '🟡 Demo mode — connect graph/workflow.py'}")
#     _md("</div>")

# _md('<div class="if-rule"></div>')

# # ── Pipeline signal chain ───────────────────────────────────────────────
# step_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
# for k in st.session_state.results:
#     step_states[k] = "done"
# render_pipeline_chain(step_states)

# # ── Trigger run ──────────────────────────────────────────────────────────
# if run_clicked:
#     if not topic.strip():
#         st.warning("Enter a research topic to start the pipeline.")
#     else:
#         st.session_state.results = {}
#         st.session_state.running = True
#         st.session_state.start_time = time.time()
#         st.session_state.elapsed = None
#         st.rerun()

# if st.session_state.running:
#     pipeline_fn = run_pipeline if LIVE_MODE else _demo_run_pipeline
#     placeholder = st.empty()
#     for step_key, payload in pipeline_fn(st.session_state.topic_input, use_rag):
#         st.session_state.results[step_key] = payload
#         with placeholder.container():
#             live_states = {k: "waiting" for k, _, _ in PIPELINE_STEPS}
#             for k in st.session_state.results:
#                 live_states[k] = "done"
#             remaining = [k for k, _, _ in PIPELINE_STEPS if k not in st.session_state.results]
#             if remaining:
#                 live_states[remaining[0]] = "running"
#             render_pipeline_chain(live_states)
#     st.session_state.elapsed = time.time() - st.session_state.start_time
#     st.session_state.running = False
#
#     verified = st.session_state.results.get("verification", {}).get("verified_sources", [])
#     storage.log_run({
#         "topic": st.session_state.topic_input,
#         "timestamp": time.time(),
#         "relevance": (
#             100 * sum(1 for s in verified if s.get("status") == "verified") / len(verified)
#             if verified else None
#         ),
#         "quality": st.session_state.results.get("critic", {}).get("score"),
#         "latency": st.session_state.elapsed,
#         "source_count": len(verified) or len(st.session_state.results.get("research", {}).get("sources", [])),
#         "report_markdown": st.session_state.results.get("writer", {}).get("report_markdown", ""),
#     })
#     st.rerun()

# # ── Metrics strip ────────────────────────────────────────────────────────
# r = st.session_state.results
# if r:
#     verified = r.get("verification", {}).get("verified_sources", [])
#     relevance = (
#         100 * sum(1 for s in verified if s.get("status") == "verified") / len(verified)
#         if verified else None
#     )
#     render_metrics({
#         "relevance": relevance,
#         "quality": r.get("critic", {}).get("score"),
#         "latency": st.session_state.elapsed,
#         "sources": len(verified) if verified else (len(r.get("research", {}).get("sources", [])) or None),
#     })

# # ── Results ──────────────────────────────────────────────────────────────
# if r:
#     tab_report, tab_sources, tab_analysis, tab_critic = st.tabs(
#         ["Report", "Sources & Verification", "Analysis", "Critic"]
#     )

#     with tab_report:
#         if "planner" in r:
#             render_subtopics(r["planner"]["subtopics"])
#         if "writer" in r:
#             render_report(r["writer"]["report_markdown"])
#             st.download_button(
#                 "⬇ Download report (.md)",
#                 data=r["writer"]["report_markdown"],
#                 file_name=f"insightforge_report_{int(time.time())}.md",
#                 mime="text/markdown",
#             )

#     with tab_sources:
#         if "research" in r:
#             render_sources(r["research"]["sources"])
#         if "verification" in r:
#             render_verification(
#                 r["verification"]["verified_sources"],
#                 r["verification"].get("conflicts", []),
#             )

#     with tab_analysis:
#         if "analysis" in r:
#             a = r["analysis"]
#             render_analysis(
#                 a.get("insights", []), a.get("trends", []),
#                 a.get("risks", []), a.get("recommendations", []),
#             )
#         else:
#             st.info("Analysis will appear once the Analysis Agent completes.")

#     with tab_critic:
#         if "critic" in r:
#             c = r["critic"]
#             render_critic(c["score"], c["feedback"], c.get("strengths", []), c.get("improvements", []))
#         else:
#             st.info("Critic review will appear once the Critic Agent completes.")

# render_footer()

"""
InsightForge — Home / Upload Document
Frontend entrypoint (root page of the multi-page app).

INTEGRATION CONTRACT for whoever wires up graph/workflow.py:

    def run_pipeline(document_text: str, use_rag: bool = True):
        '''Generator. Yields (step_key, payload) after each agent
        finishes, in this order: planner -> research -> verification
        -> analysis -> writer -> critic.'''
        yield "planner", {"subtopics": [str, ...]}
        yield "research", {"sources": [{"title","url","source_type":"web"|"rag"}, ...]}
        yield "verification", {
            "verified_sources": [{"title","url","trust_score":0-100,
                                   "status":"verified"|"conflict"|"unverified"}, ...],
            "conflicts": [str, ...],
        }
        yield "analysis", {"insights":[...], "trends":[...], "risks":[...], "recommendations":[...]}
        yield "writer", {
            "executive_summary": str,
            "key_findings": [str, ...],
            "important_concepts": [str, ...],
            "strengths": [str, ...],
            "weaknesses": [str, ...],
            "recommendations": [str, ...],
        }
        yield "critic", {"score": float, "feedback": str}

This file only handles document intake. The pipeline itself runs on
the Agent Monitor page (pages/1_🧭_Agent_Monitor.py) — that way
switching pages mid-run never loses progress, since results live in
st.session_state, which persists across pages in the same session.
"""

import streamlit as st

from ui.components import inject_css, render_header, render_sidebar
from ui.document_reader import extract_text
from tools.scraper import scrape_url

st.set_page_config(page_title="InsightForge · Home", page_icon="◆", layout="wide")
inject_css()
render_sidebar("Home")
render_header()

col_main, col_side = st.columns([2.2, 1])

with col_main:
    st.markdown('<div class="if-card-label">Upload Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )
    with st.expander("Or paste text instead"):
        pasted_text = st.text_area(
            "Pasted text", height=160, label_visibility="collapsed",
            placeholder="Paste the document's text here…",
        )
    with st.expander("Or paste a URL instead"):
        url_input = st.text_input(
            "URL", placeholder="https://example.com/article",
            label_visibility="collapsed",
        )

with col_side:
    st.markdown('<div class="if-card-label">Options</div>', unsafe_allow_html=True)
    use_rag = st.checkbox("Verify against ChromaDB + web sources", value=True)
    analyze_clicked = st.button("Analyze Document", use_container_width=True)

if analyze_clicked:
    document_text = ""
    document_name = "Pasted text"

    if uploaded_file is not None:
        try:
            document_text = extract_text(uploaded_file)
            document_name = uploaded_file.name
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")

    if not document_text.strip() and url_input.strip():
        with st.spinner("Fetching content from URL..."):
            result = scrape_url(url_input.strip())
        if result["success"] and result["content"]:
            document_text = result["content"]
            document_name = result["title"] or url_input.strip()
        else:
            st.error(f"Couldn't fetch that URL: {result.get('error', 'No content found')}")

    if not document_text.strip() and pasted_text.strip():
        document_text = pasted_text.strip()
        document_name = "Pasted text"

    if not document_text.strip():
        st.warning("Upload a document, paste some text, or enter a URL first.")
    else:
        st.session_state.document_text = document_text
        st.session_state.document_name = document_name
        st.session_state.use_rag = use_rag
        st.session_state.results = {}
        st.session_state.pipeline_done = False
        st.switch_page("pages/1_Agent_Monitor.py")

st.markdown(
    """
    <div class="if-welcome-popup">
        <h2>Uncover. Analyze. Deliver.</h2>
        <p>Intelligence that drives confident decisions. All research agents are online and ready.</p>
    </div>
    """,
    unsafe_allow_html=True
)