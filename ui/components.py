# """
# ui/components.py
# -----------------
# Presentation-only helpers for app.py. Nothing here calls the agent
# pipeline — it just renders whatever data it's handed. Keeping this
# separate means whoever wires up graph/workflow.py never has to touch
# styling, and whoever touches styling never has to understand LangGraph.

# PAYLOAD SCHEMA (what each render_* function expects) is documented
# above each function so the shapes stay obvious without cross-referencing
# app.py.
# """

# import html
# from pathlib import Path

# import streamlit as st


# def _md(content: str):
#     """Render raw HTML safely.

#     Streamlit's markdown parser treats any line indented 4+ spaces as a
#     code block. Since our HTML template strings are indented to match
#     the surrounding Python code, we strip per-line leading whitespace
#     before handing it to st.markdown — otherwise the HTML shows up as
#     literal escaped text on the page instead of rendering.
#     """
#     cleaned = "\n".join(line.strip() for line in content.strip("\n").splitlines())
#     st.markdown(cleaned, unsafe_allow_html=True)


# PIPELINE_STEPS = [
#     ("planner", "Planner", "Breaks the topic into subtopics"),
#     ("research", "Research", "Web + knowledge-base retrieval"),
#     ("verification", "Verification", "Checks source reliability"),
#     ("analysis", "Analysis", "Trends, risks, recommendations"),
#     ("writer", "Writer", "Drafts the structured report"),
#     ("critic", "Critic", "Scores and reviews the report"),
# ]


# def inject_css():
#     css_path = Path(__file__).parent / "styles.css"
#     st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# def render_header():
#     _md(
#         """
#         <div class="if-eyebrow"><span class="dot"></span>Multi-Agent Research Intelligence Platform</div>
#         <div class="if-title">Insight<span class="accent">Forge</span></div>
#         <p class="if-sub">
#             Six agents plan, retrieve, verify, analyze, write, and critique —
#             producing a cited research report with a visible trust trail,
#             not just a summary.
#         </p>
#         <div class="if-rule"></div>
#         """
#     )


# def render_pipeline_chain(step_states: dict):
#     """
#     step_states: {step_key: "waiting" | "running" | "done"}
#     step_key must match PIPELINE_STEPS keys.
#     """
#     nodes = []
#     for i, (key, name, desc) in enumerate(PIPELINE_STEPS):
#         state = step_states.get(key, "waiting")
#         label = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
#         nodes.append(
#             f"""
#             <div class="if-node {state}">
#                 <div class="if-node-line"></div>
#                 <div class="if-node-dot">{i + 1}</div>
#                 <div class="if-node-name">{name}</div>
#                 <div class="if-node-status">{label}</div>
#             </div>
#             """
#         )
#     _md(f'<div class="if-chain-wrap"><div class="if-chain">{"".join(nodes)}</div></div>')


# def render_metrics(metrics: dict):
#     """
#     metrics: {
#         "relevance": float 0-100 or None,
#         "quality": float 0-10 or None,
#         "latency": float seconds or None,
#         "sources": int or None,
#     }
#     Thresholds follow the synopsis's own success metrics.
#     """

#     def cls(val, good_min, warn_min):
#         if val is None:
#             return ""
#         if val >= good_min:
#             return "good"
#         if val >= warn_min:
#             return "warn"
#         return "bad"

#     rel = metrics.get("relevance")
#     qual = metrics.get("quality")
#     lat = metrics.get("latency")
#     src = metrics.get("sources")

#     lat_cls = "" if lat is None else ("good" if lat <= 60 else "bad")

#     cards = [
#         ("Source Relevance", f"{rel:.0f}%" if rel is not None else "—", "target ≥ 85%",
#          cls(rel, 85, 70)),
#         ("Report Quality", f"{qual:.1f}/10" if qual is not None else "—", "target ≥ 8.0",
#          cls(qual, 8, 6)),
#         ("Latency", f"{lat:.0f}s" if lat is not None else "—", "target ≤ 60s", lat_cls),
#         ("Verified Sources", f"{src}" if src is not None else "—", "target ≥ 5", ""),
#     ]
#     parts = [
#         f"""
#         <div class="if-metric">
#             <div class="if-metric-label">{label}</div>
#             <div class="if-metric-value {c}">{value}</div>
#             <div class="if-metric-target">{target}</div>
#         </div>
#         """
#         for label, value, target, c in cards
#     ]
#     _md(f'<div class="if-metrics">{"".join(parts)}</div>')


# def render_panel_open(title: str, accent: str = "signal"):
#     _md(f'<div class="if-panel"><div class="if-panel-head"><span class="accent-{accent}">{title}</span></div>')


# def render_panel_close():
#     _md("</div>")


# def render_subtopics(subtopics: list[str]):
#     render_panel_open("01 · Planner — Subtopics", "signal")
#     rows = "".join(
#         f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(s)}</div>'
#         for s in subtopics
#     )
#     _md(rows or '<div class="if-row">No subtopics generated.</div>')
#     render_panel_close()


# def render_sources(sources: list[dict]):
#     """
#     sources: [{"title": str, "url": str, "source_type": "web"|"rag"}]
#     """
#     render_panel_open("02 · Research — Retrieved Sources", "signal")
#     if not sources:
#         _md('<div class="if-row">No sources retrieved yet.</div>')
#     for s in sources:
#         tag_cls = "rag" if s.get("source_type") == "rag" else "web"
#         tag_label = "RAG" if s.get("source_type") == "rag" else "WEB"
#         _md(
#             f"""
#             <div class="if-source">
#                 <span class="if-tag {tag_cls}">{tag_label}</span>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#             </div>
#             """
#         )
#     render_panel_close()


# def render_verification(verified_sources: list[dict], conflicts: list[str]):
#     """
#     verified_sources: [{"title","url","trust_score":0-100,"status":"verified"|"conflict"|"unverified"}]
#     """
#     render_panel_open("03 · Verification — Trust Ledger", "signal")
#     color_map = {"verified": "#5eead4", "conflict": "#f87171", "unverified": "#8b93a7"}
#     for s in verified_sources:
#         status = s.get("status", "unverified")
#         score = s.get("trust_score", 0)
#         bar_color = color_map.get(status, "#8b93a7")
#         _md(
#             f"""
#             <div class="if-source">
#                 <div class="if-trust-bar-track">
#                     <div class="if-trust-bar-fill" style="width:{score}%;background:{bar_color};"></div>
#                 </div>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#                 <span class="if-trust-tag {status}">{score:.0f}%</span>
#             </div>
#             """
#         )
#     if conflicts:
#         _md('<div style="height:0.6rem;"></div>')
#         for c in conflicts:
#             _md(
#                 f'<div class="if-row"><span class="if-row-marker" style="color:#f87171;">⚠</span>{html.escape(c)}</div>'
#             )
#     render_panel_close()


# def render_analysis(insights: list[str], trends: list[str], risks: list[str], recommendations: list[str]):
#     render_panel_open("04 · Analysis — Insights & Risk", "insight")
#     for label, items in [
#         ("Trends", trends), ("Risks", risks),
#         ("Insights", insights), ("Recommendations", recommendations),
#     ]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:#a78bfa;margin:0.6rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_report(report_markdown: str):
#     render_panel_open("05 · Writer — Research Report", "signal")
#     _md('<div class="if-report">')
#     st.markdown(report_markdown)  # the report itself is normal markdown, not raw HTML
#     _md("</div>")
#     render_panel_close()


# def render_critic(score: float, feedback: str, strengths: list[str], improvements: list[str]):
#     render_panel_open("06 · Critic — Review", "review")
#     _md(
#         f"""
#         <div class="if-score-wrap">
#             <div><span class="if-score-num">{score:.1f}</span><span class="if-score-den">/10</span></div>
#             <div style="color:#8b93a7;font-size:0.85rem;line-height:1.6;">{html.escape(feedback)}</div>
#         </div>
#         """
#     )
#     if strengths or improvements:
#         _md('<div style="height:0.8rem;"></div>')
#     for label, items, color in [("Strengths", strengths, "#5eead4"), ("To improve", improvements, "#fbbf24")]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:{color};margin:0.5rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_footer():
#     _md('<div class="if-footer">AgentHive · LangGraph multi-agent pipeline · ChromaDB RAG · Streamlit</div>')



# """
# ui/components.py
# -----------------
# Presentation-only helpers for app.py. Nothing here calls the agent
# pipeline — it just renders whatever data it's handed. Keeping this
# separate means whoever wires up graph/workflow.py never has to touch
# styling, and whoever touches styling never has to understand LangGraph.

# PAYLOAD SCHEMA (what each render_* function expects) is documented
# above each function so the shapes stay obvious without cross-referencing
# app.py.
# """

# import html
# from pathlib import Path

# import streamlit as st


# def _md(content: str):
#     """Render raw HTML safely.

#     Streamlit's markdown parser treats any line indented 4+ spaces as a
#     code block. Since our HTML template strings are indented to match
#     the surrounding Python code, we strip per-line leading whitespace
#     before handing it to st.markdown — otherwise the HTML shows up as
#     literal escaped text on the page instead of rendering.
#     """
#     cleaned = "\n".join(line.strip() for line in content.strip("\n").splitlines())
#     st.markdown(cleaned, unsafe_allow_html=True)


# PIPELINE_STEPS = [
#     ("planner", "Planner", "Breaks the topic into subtopics"),
#     ("research", "Research", "Web + knowledge-base retrieval"),
#     ("verification", "Verification", "Checks source reliability"),
#     ("analysis", "Analysis", "Trends, risks, recommendations"),
#     ("writer", "Writer", "Drafts the structured report"),
#     ("critic", "Critic", "Scores and reviews the report"),
# ]


# def inject_css():
#     css_path = Path(__file__).parent / "styles.css"
#     st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# def render_header():
#     _md(
#         """
#         <div class="if-eyebrow"><span class="dot"></span>Multi-Agent Research Intelligence Platform</div>
#         <div class="if-title">Insight<span class="accent">Forge</span></div>
#         <p class="if-sub">
#             Six agents plan, retrieve, verify, analyze, write, and critique —
#             producing a cited research report with a visible trust trail,
#             not just a summary.
#         </p>
#         <div class="if-rule"></div>
#         """
#     )


# def render_pipeline_chain(step_states: dict):
#     """
#     step_states: {step_key: "waiting" | "running" | "done"}
#     step_key must match PIPELINE_STEPS keys.
#     """
#     nodes = []
#     for i, (key, name, desc) in enumerate(PIPELINE_STEPS):
#         state = step_states.get(key, "waiting")
#         label = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
#         nodes.append(
#             f"""
#             <div class="if-node {state}">
#                 <div class="if-node-line"></div>
#                 <div class="if-node-dot">{i + 1}</div>
#                 <div class="if-node-name">{name}</div>
#                 <div class="if-node-status">{label}</div>
#             </div>
#             """
#         )
#     _md(f'<div class="if-chain-wrap"><div class="if-chain">{"".join(nodes)}</div></div>')


# def render_metrics(metrics: dict):
#     """
#     metrics: {
#         "relevance": float 0-100 or None,
#         "quality": float 0-10 or None,
#         "latency": float seconds or None,
#         "sources": int or None,
#     }
#     Thresholds follow the synopsis's own success metrics.
#     """

#     def cls(val, good_min, warn_min):
#         if val is None:
#             return ""
#         if val >= good_min:
#             return "good"
#         if val >= warn_min:
#             return "warn"
#         return "bad"

#     rel = metrics.get("relevance")
#     qual = metrics.get("quality")
#     lat = metrics.get("latency")
#     src = metrics.get("sources")

#     lat_cls = "" if lat is None else ("good" if lat <= 60 else "bad")

#     cards = [
#         ("Source Relevance", f"{rel:.0f}%" if rel is not None else "—", "target ≥ 85%",
#          cls(rel, 85, 70)),
#         ("Report Quality", f"{qual:.1f}/10" if qual is not None else "—", "target ≥ 8.0",
#          cls(qual, 8, 6)),
#         ("Latency", f"{lat:.0f}s" if lat is not None else "—", "target ≤ 60s", lat_cls),
#         ("Verified Sources", f"{src}" if src is not None else "—", "target ≥ 5", ""),
#     ]
#     parts = [
#         f"""
#         <div class="if-metric">
#             <div class="if-metric-label">{label}</div>
#             <div class="if-metric-value {c}">{value}</div>
#             <div class="if-metric-target">{target}</div>
#         </div>
#         """
#         for label, value, target, c in cards
#     ]
#     _md(f'<div class="if-metrics">{"".join(parts)}</div>')


# def render_panel_open(title: str, accent: str = "signal"):
#     _md(f'<div class="if-panel"><div class="if-panel-head"><span class="accent-{accent}">{title}</span></div>')


# def render_panel_close():
#     _md("</div>")


# def render_subtopics(subtopics: list[str]):
#     render_panel_open("01 · Planner — Subtopics", "signal")
#     rows = "".join(
#         f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(s)}</div>'
#         for s in subtopics
#     )
#     _md(rows or '<div class="if-row">No subtopics generated.</div>')
#     render_panel_close()


# def render_sources(sources: list[dict]):
#     """
#     sources: [{"title": str, "url": str, "source_type": "web"|"rag"}]
#     """
#     render_panel_open("02 · Research — Retrieved Sources", "signal")
#     if not sources:
#         _md('<div class="if-row">No sources retrieved yet.</div>')
#     for s in sources:
#         tag_cls = "rag" if s.get("source_type") == "rag" else "web"
#         tag_label = "RAG" if s.get("source_type") == "rag" else "WEB"
#         _md(
#             f"""
#             <div class="if-source">
#                 <span class="if-tag {tag_cls}">{tag_label}</span>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#             </div>
#             """
#         )
#     render_panel_close()


# def render_verification(verified_sources: list[dict], conflicts: list[str]):
#     """
#     verified_sources: [{"title","url","trust_score":0-100,"status":"verified"|"conflict"|"unverified"}]
#     """
#     render_panel_open("03 · Verification — Trust Ledger", "signal")
#     color_map = {"verified": "var(--signal)", "conflict": "var(--alert)", "unverified": "var(--text-faint)"}
#     for s in verified_sources:
#         status = s.get("status", "unverified")
#         score = s.get("trust_score", 0)
#         bar_color = color_map.get(status, "#8b93a7")
#         _md(
#             f"""
#             <div class="if-source">
#                 <div class="if-trust-bar-track">
#                     <div class="if-trust-bar-fill" style="width:{score}%;background:{bar_color};"></div>
#                 </div>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#                 <span class="if-trust-tag {status}">{score:.0f}%</span>
#             </div>
#             """
#         )
#     if conflicts:
#         _md('<div style="height:0.6rem;"></div>')
#         for c in conflicts:
#             _md(
#                 f'<div class="if-row"><span class="if-row-marker" style="color:var(--alert);">⚠</span>{html.escape(c)}</div>'
#             )
#     render_panel_close()


# def render_analysis(insights: list[str], trends: list[str], risks: list[str], recommendations: list[str]):
#     render_panel_open("04 · Analysis — Insights & Risk", "insight")
#     for label, items in [
#         ("Trends", trends), ("Risks", risks),
#         ("Insights", insights), ("Recommendations", recommendations),
#     ]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:var(--insight);margin:0.6rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_report(report_markdown: str):
#     render_panel_open("05 · Writer — Research Report", "signal")
#     _md('<div class="if-report">')
#     st.markdown(report_markdown)  # the report itself is normal markdown, not raw HTML
#     _md("</div>")
#     render_panel_close()


# def render_critic(score: float, feedback: str, strengths: list[str], improvements: list[str]):
#     render_panel_open("06 · Critic — Review", "review")
#     _md(
#         f"""
#         <div class="if-score-wrap">
#             <div><span class="if-score-num">{score:.1f}</span><span class="if-score-den">/10</span></div>
#             <div style="color:var(--text-dim);font-size:0.85rem;line-height:1.6;">{html.escape(feedback)}</div>
#         </div>
#         """
#     )
#     if strengths or improvements:
#         _md('<div style="height:0.8rem;"></div>')
#     for label, items, color in [("Strengths", strengths, "var(--signal)"), ("To improve", improvements, "var(--review)")]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:{color};margin:0.5rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_page_header(eyebrow: str, title: str, subtitle: str = ""):
#     """Compact version of render_header(), for pages other than the main dashboard."""
#     sub_html = f'<p class="if-sub">{html.escape(subtitle)}</p>' if subtitle else ""
#     _md(
#         f"""
#         <div class="if-eyebrow"><span class="dot"></span>{html.escape(eyebrow)}</div>
#         <div class="if-title" style="font-size:2rem;">{title}</div>
#         {sub_html}
#         <div class="if-rule"></div>
#         """
#     )


# def render_footer():
#     _md('<div class="if-footer">AgentHive · LangGraph multi-agent pipeline · ChromaDB RAG · Streamlit</div>')


# """
# ui/components.py
# -----------------
# Presentation-only helpers for app.py. Nothing here calls the agent
# pipeline — it just renders whatever data it's handed. Keeping this
# separate means whoever wires up graph/workflow.py never has to touch
# styling, and whoever touches styling never has to understand LangGraph.

# PAYLOAD SCHEMA (what each render_* function expects) is documented
# above each function so the shapes stay obvious without cross-referencing
# app.py.
# """

# import html
# from pathlib import Path

# import streamlit as st


# def _md(content: str):
#     """Render raw HTML safely.

#     Streamlit's markdown parser treats any line indented 4+ spaces as a
#     code block. Since our HTML template strings are indented to match
#     the surrounding Python code, we strip per-line leading whitespace
#     before handing it to st.markdown — otherwise the HTML shows up as
#     literal escaped text on the page instead of rendering.
#     """
#     cleaned = "\n".join(line.strip() for line in content.strip("\n").splitlines())
#     st.markdown(cleaned, unsafe_allow_html=True)


# PIPELINE_STEPS = [
#     ("planner", "Planner", "Breaks the topic into subtopics"),
#     ("research", "Research", "Web + knowledge-base retrieval"),
#     ("verification", "Verification", "Checks source reliability"),
#     ("analysis", "Analysis", "Trends, risks, recommendations"),
#     ("writer", "Writer", "Drafts the structured report"),
#     ("critic", "Critic", "Scores and reviews the report"),
# ]


# def inject_css():
#     css_path = Path(__file__).parent / "styles.css"
#     st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# def render_header():
#     _md(
#         """
#         <div class="if-eyebrow"><span class="dot"></span>Multi-Agent Research Intelligence Platform</div>
#         <div class="if-title">Insight<span class="accent">Forge</span></div>
#         <p class="if-sub">
#             Six agents plan, retrieve, verify, analyze, write, and critique —
#             producing a cited research report with a visible trust trail,
#             not just a summary.
#         </p>
#         <div class="if-rule"></div>
#         """
#     )


# def render_pipeline_chain(step_states: dict):
#     """
#     step_states: {step_key: "waiting" | "running" | "done"}
#     step_key must match PIPELINE_STEPS keys.
#     """
#     nodes = []
#     for i, (key, name, desc) in enumerate(PIPELINE_STEPS):
#         state = step_states.get(key, "waiting")
#         label = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
#         nodes.append(
#             f"""
#             <div class="if-node {state}">
#                 <div class="if-node-line"></div>
#                 <div class="if-node-dot">{i + 1}</div>
#                 <div class="if-node-name">{name}</div>
#                 <div class="if-node-status">{label}</div>
#             </div>
#             """
#         )
#     _md(f'<div class="if-chain-wrap"><div class="if-chain">{"".join(nodes)}</div></div>')


# def render_metrics(metrics: dict):
#     """
#     metrics: {
#         "relevance": float 0-100 or None,
#         "quality": float 0-10 or None,
#         "latency": float seconds or None,
#         "sources": int or None,
#     }
#     Thresholds follow the synopsis's own success metrics.
#     """

#     def cls(val, good_min, warn_min):
#         if val is None:
#             return ""
#         if val >= good_min:
#             return "good"
#         if val >= warn_min:
#             return "warn"
#         return "bad"

#     rel = metrics.get("relevance")
#     qual = metrics.get("quality")
#     lat = metrics.get("latency")
#     src = metrics.get("sources")

#     lat_cls = "" if lat is None else ("good" if lat <= 60 else "bad")

#     cards = [
#         ("Source Relevance", f"{rel:.0f}%" if rel is not None else "—", "target ≥ 85%",
#          cls(rel, 85, 70)),
#         ("Report Quality", f"{qual:.1f}/10" if qual is not None else "—", "target ≥ 8.0",
#          cls(qual, 8, 6)),
#         ("Latency", f"{lat:.0f}s" if lat is not None else "—", "target ≤ 60s", lat_cls),
#         ("Verified Sources", f"{src}" if src is not None else "—", "target ≥ 5", ""),
#     ]
#     parts = [
#         f"""
#         <div class="if-metric">
#             <div class="if-metric-label">{label}</div>
#             <div class="if-metric-value {c}">{value}</div>
#             <div class="if-metric-target">{target}</div>
#         </div>
#         """
#         for label, value, target, c in cards
#     ]
#     _md(f'<div class="if-metrics">{"".join(parts)}</div>')


# def render_panel_open(title: str, accent: str = "signal"):
#     _md(f'<div class="if-panel"><div class="if-panel-head"><span class="accent-{accent}">{title}</span></div>')


# def render_panel_close():
#     _md("</div>")


# def render_subtopics(subtopics: list[str]):
#     render_panel_open("01 · Planner — Subtopics", "signal")
#     rows = "".join(
#         f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(s)}</div>'
#         for s in subtopics
#     )
#     _md(rows or '<div class="if-row">No subtopics generated.</div>')
#     render_panel_close()


# def render_sources(sources: list[dict]):
#     """
#     sources: [{"title": str, "url": str, "source_type": "web"|"rag"}]
#     """
#     render_panel_open("02 · Research — Retrieved Sources", "signal")
#     if not sources:
#         _md('<div class="if-row">No sources retrieved yet.</div>')
#     for s in sources:
#         tag_cls = "rag" if s.get("source_type") == "rag" else "web"
#         tag_label = "RAG" if s.get("source_type") == "rag" else "WEB"
#         _md(
#             f"""
#             <div class="if-source">
#                 <span class="if-tag {tag_cls}">{tag_label}</span>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#             </div>
#             """
#         )
#     render_panel_close()


# def render_verification(verified_sources: list[dict], conflicts: list[str]):
#     """
#     verified_sources: [{"title","url","trust_score":0-100,"status":"verified"|"conflict"|"unverified"}]
#     """
#     render_panel_open("03 · Verification — Trust Ledger", "signal")
#     color_map = {"verified": "#5eead4", "conflict": "#f87171", "unverified": "#8b93a7"}
#     for s in verified_sources:
#         status = s.get("status", "unverified")
#         score = s.get("trust_score", 0)
#         bar_color = color_map.get(status, "#8b93a7")
#         _md(
#             f"""
#             <div class="if-source">
#                 <div class="if-trust-bar-track">
#                     <div class="if-trust-bar-fill" style="width:{score}%;background:{bar_color};"></div>
#                 </div>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#                 <span class="if-trust-tag {status}">{score:.0f}%</span>
#             </div>
#             """
#         )
#     if conflicts:
#         _md('<div style="height:0.6rem;"></div>')
#         for c in conflicts:
#             _md(
#                 f'<div class="if-row"><span class="if-row-marker" style="color:#f87171;">⚠</span>{html.escape(c)}</div>'
#             )
#     render_panel_close()


# def render_analysis(insights: list[str], trends: list[str], risks: list[str], recommendations: list[str]):
#     render_panel_open("04 · Analysis — Insights & Risk", "insight")
#     for label, items in [
#         ("Trends", trends), ("Risks", risks),
#         ("Insights", insights), ("Recommendations", recommendations),
#     ]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:#a78bfa;margin:0.6rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_report(report_markdown: str):
#     render_panel_open("05 · Writer — Research Report", "signal")
#     _md('<div class="if-report">')
#     st.markdown(report_markdown)  # the report itself is normal markdown, not raw HTML
#     _md("</div>")
#     render_panel_close()


# def render_critic(score: float, feedback: str, strengths: list[str], improvements: list[str]):
#     render_panel_open("06 · Critic — Review", "review")
#     _md(
#         f"""
#         <div class="if-score-wrap">
#             <div><span class="if-score-num">{score:.1f}</span><span class="if-score-den">/10</span></div>
#             <div style="color:#8b93a7;font-size:0.85rem;line-height:1.6;">{html.escape(feedback)}</div>
#         </div>
#         """
#     )
#     if strengths or improvements:
#         _md('<div style="height:0.8rem;"></div>')
#     for label, items, color in [("Strengths", strengths, "#5eead4"), ("To improve", improvements, "#fbbf24")]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:{color};margin:0.5rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_footer():
#     _md('<div class="if-footer">AgentHive · LangGraph multi-agent pipeline · ChromaDB RAG · Streamlit</div>')



# """
# ui/components.py
# -----------------
# Presentation-only helpers for app.py. Nothing here calls the agent
# pipeline — it just renders whatever data it's handed. Keeping this
# separate means whoever wires up graph/workflow.py never has to touch
# styling, and whoever touches styling never has to understand LangGraph.

# PAYLOAD SCHEMA (what each render_* function expects) is documented
# above each function so the shapes stay obvious without cross-referencing
# app.py.
# """

# import html
# from pathlib import Path

# import streamlit as st


# def _md(content: str):
#     """Render raw HTML safely.

#     Streamlit's markdown parser treats any line indented 4+ spaces as a
#     code block. Since our HTML template strings are indented to match
#     the surrounding Python code, we strip per-line leading whitespace
#     before handing it to st.markdown — otherwise the HTML shows up as
#     literal escaped text on the page instead of rendering.
#     """
#     cleaned = "\n".join(line.strip() for line in content.strip("\n").splitlines())
#     st.markdown(cleaned, unsafe_allow_html=True)


# PIPELINE_STEPS = [
#     ("planner", "Planner", "Breaks the topic into subtopics"),
#     ("research", "Research", "Web + knowledge-base retrieval"),
#     ("verification", "Verification", "Checks source reliability"),
#     ("analysis", "Analysis", "Trends, risks, recommendations"),
#     ("writer", "Writer", "Drafts the structured report"),
#     ("critic", "Critic", "Scores and reviews the report"),
# ]


# def inject_css():
#     css_path = Path(__file__).parent / "styles.css"
#     st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# def render_header():
#     _md(
#         """
#         <div class="if-eyebrow"><span class="dot"></span>Multi-Agent Research Intelligence Platform</div>
#         <div class="if-title">Insight<span class="accent">Forge</span></div>
#         <p class="if-sub">
#             Six agents plan, retrieve, verify, analyze, write, and critique —
#             producing a cited research report with a visible trust trail,
#             not just a summary.
#         </p>
#         <div class="if-rule"></div>
#         """
#     )


# def render_pipeline_chain(step_states: dict):
#     """
#     step_states: {step_key: "waiting" | "running" | "done"}
#     step_key must match PIPELINE_STEPS keys.
#     """
#     nodes = []
#     for i, (key, name, desc) in enumerate(PIPELINE_STEPS):
#         state = step_states.get(key, "waiting")
#         label = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
#         nodes.append(
#             f"""
#             <div class="if-node {state}">
#                 <div class="if-node-line"></div>
#                 <div class="if-node-dot">{i + 1}</div>
#                 <div class="if-node-name">{name}</div>
#                 <div class="if-node-status">{label}</div>
#             </div>
#             """
#         )
#     _md(f'<div class="if-chain-wrap"><div class="if-chain">{"".join(nodes)}</div></div>')


# def render_metrics(metrics: dict):
#     """
#     metrics: {
#         "relevance": float 0-100 or None,
#         "quality": float 0-10 or None,
#         "latency": float seconds or None,
#         "sources": int or None,
#     }
#     Thresholds follow the synopsis's own success metrics.
#     """

#     def cls(val, good_min, warn_min):
#         if val is None:
#             return ""
#         if val >= good_min:
#             return "good"
#         if val >= warn_min:
#             return "warn"
#         return "bad"

#     rel = metrics.get("relevance")
#     qual = metrics.get("quality")
#     lat = metrics.get("latency")
#     src = metrics.get("sources")

#     lat_cls = "" if lat is None else ("good" if lat <= 60 else "bad")

#     cards = [
#         ("Source Relevance", f"{rel:.0f}%" if rel is not None else "—", "target ≥ 85%",
#          cls(rel, 85, 70)),
#         ("Report Quality", f"{qual:.1f}/10" if qual is not None else "—", "target ≥ 8.0",
#          cls(qual, 8, 6)),
#         ("Latency", f"{lat:.0f}s" if lat is not None else "—", "target ≤ 60s", lat_cls),
#         ("Verified Sources", f"{src}" if src is not None else "—", "target ≥ 5", ""),
#     ]
#     parts = [
#         f"""
#         <div class="if-metric">
#             <div class="if-metric-label">{label}</div>
#             <div class="if-metric-value {c}">{value}</div>
#             <div class="if-metric-target">{target}</div>
#         </div>
#         """
#         for label, value, target, c in cards
#     ]
#     _md(f'<div class="if-metrics">{"".join(parts)}</div>')


# def render_panel_open(title: str, accent: str = "signal"):
#     _md(f'<div class="if-panel"><div class="if-panel-head"><span class="accent-{accent}">{title}</span></div>')


# def render_panel_close():
#     _md("</div>")


# def render_subtopics(subtopics: list[str]):
#     render_panel_open("01 · Planner — Subtopics", "signal")
#     rows = "".join(
#         f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(s)}</div>'
#         for s in subtopics
#     )
#     _md(rows or '<div class="if-row">No subtopics generated.</div>')
#     render_panel_close()


# def render_sources(sources: list[dict]):
#     """
#     sources: [{"title": str, "url": str, "source_type": "web"|"rag"}]
#     """
#     render_panel_open("02 · Research — Retrieved Sources", "signal")
#     if not sources:
#         _md('<div class="if-row">No sources retrieved yet.</div>')
#     for s in sources:
#         tag_cls = "rag" if s.get("source_type") == "rag" else "web"
#         tag_label = "RAG" if s.get("source_type") == "rag" else "WEB"
#         _md(
#             f"""
#             <div class="if-source">
#                 <span class="if-tag {tag_cls}">{tag_label}</span>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#             </div>
#             """
#         )
#     render_panel_close()


# def render_verification(verified_sources: list[dict], conflicts: list[str]):
#     """
#     verified_sources: [{"title","url","trust_score":0-100,"status":"verified"|"conflict"|"unverified"}]
#     """
#     render_panel_open("03 · Verification — Trust Ledger", "signal")
#     color_map = {"verified": "var(--signal)", "conflict": "var(--alert)", "unverified": "var(--text-faint)"}
#     for s in verified_sources:
#         status = s.get("status", "unverified")
#         score = s.get("trust_score", 0)
#         bar_color = color_map.get(status, "#8b93a7")
#         _md(
#             f"""
#             <div class="if-source">
#                 <div class="if-trust-bar-track">
#                     <div class="if-trust-bar-fill" style="width:{score}%;background:{bar_color};"></div>
#                 </div>
#                 <div class="if-source-body">
#                     <div class="if-source-title">{html.escape(s.get('title', 'Untitled'))}</div>
#                     <div class="if-source-url">{html.escape(s.get('url', ''))}</div>
#                 </div>
#                 <span class="if-trust-tag {status}">{score:.0f}%</span>
#             </div>
#             """
#         )
#     if conflicts:
#         _md('<div style="height:0.6rem;"></div>')
#         for c in conflicts:
#             _md(
#                 f'<div class="if-row"><span class="if-row-marker" style="color:var(--alert);">⚠</span>{html.escape(c)}</div>'
#             )
#     render_panel_close()


# def render_analysis(insights: list[str], trends: list[str], risks: list[str], recommendations: list[str]):
#     render_panel_open("04 · Analysis — Insights & Risk", "insight")
#     for label, items in [
#         ("Trends", trends), ("Risks", risks),
#         ("Insights", insights), ("Recommendations", recommendations),
#     ]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:var(--insight);margin:0.6rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_report(report_markdown: str):
#     render_panel_open("05 · Writer — Research Report", "signal")
#     _md('<div class="if-report">')
#     st.markdown(report_markdown)  # the report itself is normal markdown, not raw HTML
#     _md("</div>")
#     render_panel_close()


# def render_critic(score: float, feedback: str, strengths: list[str], improvements: list[str]):
#     render_panel_open("06 · Critic — Review", "review")
#     _md(
#         f"""
#         <div class="if-score-wrap">
#             <div><span class="if-score-num">{score:.1f}</span><span class="if-score-den">/10</span></div>
#             <div style="color:var(--text-dim);font-size:0.85rem;line-height:1.6;">{html.escape(feedback)}</div>
#         </div>
#         """
#     )
#     if strengths or improvements:
#         _md('<div style="height:0.8rem;"></div>')
#     for label, items, color in [("Strengths", strengths, "var(--signal)"), ("To improve", improvements, "var(--review)")]:
#         if not items:
#             continue
#         _md(
#             f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
#             f'letter-spacing:0.1em;text-transform:uppercase;color:{color};margin:0.5rem 0 0.2rem;">{label}</div>'
#         )
#         rows = "".join(
#             f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>'
#             for i in items
#         )
#         _md(rows)
#     render_panel_close()


# def render_page_header(eyebrow: str, title: str, subtitle: str = ""):
#     """Compact version of render_header(), for pages other than the main dashboard."""
#     sub_html = f'<p class="if-sub">{html.escape(subtitle)}</p>' if subtitle else ""
#     _md(
#         f"""
#         <div class="if-eyebrow"><span class="dot"></span>{html.escape(eyebrow)}</div>
#         <div class="if-title" style="font-size:2rem;">{title}</div>
#         {sub_html}
#         <div class="if-rule"></div>
#         """
#     )


# def render_footer():
#     _md('<div class="if-footer">AgentHive · LangGraph multi-agent pipeline · ChromaDB RAG · Streamlit</div>')


"""
ui/components.py
-----------------
Presentation-only helpers for app.py and the pages/ scripts. Nothing
here calls the agent pipeline — it just renders whatever data it's
handed.

PAYLOAD SCHEMA (what each render_* function expects) is documented
above each function so the shapes stay obvious without cross-referencing
the page files.
"""
import html
from pathlib import Path

import streamlit as st


def _md(content: str):
    """Render raw HTML safely.

    Streamlit's markdown parser treats any line indented 4+ spaces as a
    code block, so we strip per-line leading whitespace first.

    IMPORTANT: build a panel's ENTIRE inner HTML as one string and pass
    it to a single _md() call. Each st.markdown() call is parsed by the
    browser independently — if you open a <div> in one call and close
    it in a later call, the browser auto-closes the unclosed div at the
    end of THAT call's own fragment, and the later call's content ends
    up as an unstyled sibling instead of nested inside it. (This bit an
    earlier version of render_sources/render_verification/render_analysis
    — fixed below by having each of them build one big string via
    render_panel() instead of open/loop/close across separate calls.)
    """
    cleaned = "\n".join(line.strip() for line in content.strip("\n").splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


PIPELINE_STEPS = [
    ("planner", "Planner", "Breaks the document into subtopics to analyze"),
    ("research", "Research", "Gathers supporting web + knowledge-base context"),
    ("verification", "Verification", "Checks reliability of that supporting context"),
    ("analysis", "Analysis", "Surfaces trends, risks, and insights"),
    ("writer", "Writer", "Drafts the structured report"),
    ("critic", "Critic", "Scores and reviews the report"),
]

NAV_PAGES = [
    ("app.py", "Home", "🏠"),
    ("pages/1_Agent_Monitor.py", "Agent Monitor", "🧭"),
    ("pages/2_Analysis_Dashboard.py", "Analysis Dashboard", "📊"),
    ("pages/3_Final_Report.py", "Final Report", "📄"),
]


def inject_css():
    css_path = Path(__file__).parent / "styles.css"
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def render_navbar():
    """Horizontal top nav (in addition to Streamlit's automatic sidebar
    page list), using st.page_link. Requires Streamlit >= 1.31 —
    `pip install --upgrade streamlit` if this errors."""
    cols = st.columns(len(NAV_PAGES))
    for col, (path, label, icon) in zip(cols, NAV_PAGES):
        with col:
            st.page_link(path, label=label, icon=icon, use_container_width=True)
    _md('<div class="if-rule"></div>')


def render_sidebar(active_label: str):
    """Custom branded left sidebar, replaces Streamlit's default page list.
    active_label: current page's label from NAV_PAGES, to highlight it.

    Also renders a "Recent Runs" search-history list underneath the nav
    links, backed by ui/history_storage.py (a flat JSON file on disk).
    Clicking a past run reloads its full results into session_state and
    jumps to the Final Report page.
    """
    from ui.history_storage import load_history  # local import avoids circulars

    with st.sidebar:
        _md(
            """
            <div class="if-sidebar-brand">
                <div class="if-sidebar-brand-mark">AH</div>
                <div class="if-sidebar-brand-name">Insight<span class="accent">Forge</span></div>
            </div>
            """
        )
        for path, label, icon in NAV_PAGES:
            wrapper_class = "if-sidebar-active" if label == active_label else ""
            st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
            st.page_link(path, label=label, icon=icon, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Search History ───────────────────────────────────────────
        # Shows the last 10 completed pipeline runs. Each entry is saved
        # by pages/1_Agent_Monitor.py right after the pipeline finishes,
        # and stores the FULL results dict (scores, sources, report —
        # everything), not just the query/title.
        _md('<div class="if-sidebar-footer" style="margin-top:1rem;">Recent Runs</div>')
        history = load_history()
        if not history:
            st.caption("No past runs yet.")
        else:
            import datetime
            for entry in history[:10]:
                ts = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime("%d %b, %H:%M")
                label_text = entry["document_name"][:28]
                if st.button(f"📄 {label_text}\n{ts}", key=f"hist_{entry['id']}", use_container_width=True):
                    # Reload this past run's full results into the
                    # current session and jump straight to the report.
                    st.session_state.results = entry["results"]
                    st.session_state.document_name = entry["document_name"]
                    st.session_state.elapsed = entry.get("elapsed")
                    st.session_state.pipeline_done = True
                    st.switch_page("pages/3_Final_Report.py")

        _md(
            '<div class="if-sidebar-footer">AgentHive<br>LangGraph · ChromaDB RAG</div>'
        )


def render_header():
    _md(
        """
        <div class="if-header-wrap">
            <svg class="if-hero-net" viewBox="0 0 520 380" xmlns="http://www.w3.org/2000/svg">
                <g stroke="#a78bfa" stroke-width="1" opacity="0.55">
                    <line x1="40" y1="60" x2="140" y2="110"/>
                    <line x1="140" y1="110" x2="120" y2="220"/>
                    <line x1="140" y1="110" x2="260" y2="90"/>
                    <line x1="260" y1="90" x2="360" y2="140"/>
                    <line x1="360" y1="140" x2="420" y2="80"/>
                    <line x1="360" y1="140" x2="440" y2="220"/>
                    <line x1="260" y1="90" x2="300" y2="200"/>
                    <line x1="300" y1="200" x2="220" y2="260"/>
                    <line x1="120" y1="220" x2="220" y2="260"/>
                    <line x1="220" y1="260" x2="320" y2="320"/>
                    <line x1="440" y1="220" x2="480" y2="310"/>
                    <line x1="320" y1="320" x2="440" y2="220"/>
                    <line x1="40" y1="60" x2="90" y2="160"/>
                    <line x1="90" y1="160" x2="120" y2="220"/>
                    <line x1="480" y1="80" x2="420" y2="80"/>
                </g>
                <g fill="#c4b5fd">
                    <circle cx="40" cy="60" r="3"/>
                    <circle cx="140" cy="110" r="4"/>
                    <circle cx="120" cy="220" r="3"/>
                    <circle cx="260" cy="90" r="5"/>
                    <circle cx="360" cy="140" r="4"/>
                    <circle cx="420" cy="80" r="3"/>
                    <circle cx="440" cy="220" r="4"/>
                    <circle cx="300" cy="200" r="3"/>
                    <circle cx="220" cy="260" r="4"/>
                    <circle cx="320" cy="320" r="3"/>
                    <circle cx="480" cy="310" r="3"/>
                    <circle cx="90" cy="160" r="3"/>
                    <circle cx="480" cy="80" r="3"/>
                </g>
            </svg>
            <div class="if-header-content">
                <div class="if-eyebrow"><span class="dot"></span>Multi-Agent Research Intelligence Platform</div>
                <div class="if-title">Insight<span class="accent">Forge</span></div>
                <p class="if-sub">
                    Upload a document and six agents plan, retrieve, verify, analyze,
                    write, and critique — producing a structured analysis with a
                    visible trust trail, not just a summary.
                </p>
                <div class="if-rule"></div>
            </div>
        </div>
        """
    )


def render_page_header(eyebrow: str, title: str, subtitle: str = ""):
    """Compact version of render_header(), for pages other than Home."""
    sub_html = f'<p class="if-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    _md(
        f"""
        <div class="if-eyebrow"><span class="dot"></span>{html.escape(eyebrow)}</div>
        <div class="if-title" style="font-size:2rem;">{title}</div>
        {sub_html}
        <div class="if-rule"></div>
        """
    )


def render_pipeline_chain(step_states: dict):
    """step_states: {step_key: "waiting" | "running" | "done"}."""
    nodes = []
    for i, (key, name, desc) in enumerate(PIPELINE_STEPS):
        state = step_states.get(key, "waiting")
        label = {"waiting": "Waiting", "running": "Running", "done": "Done"}[state]
        nodes.append(
            f"""
            <div class="if-node {state}">
                <div class="if-node-line"></div>
                <div class="if-node-dot">{i + 1}</div>
                <div class="if-node-name">{name}</div>
                <div class="if-node-status">{label}</div>
            </div>
            """
        )
    _md(f'<div class="if-chain-wrap"><div class="if-chain">{"".join(nodes)}</div></div>')


def render_agent_status_list(step_states: dict):
    """The 'Agent Name ✅ Completed' checklist for the Agent Monitor page."""
    icon = {"waiting": "⏳", "running": "🔄", "done": "✅"}
    label = {"waiting": "Waiting", "running": "Running", "done": "Completed"}
    rows = []
    for key, name, desc in PIPELINE_STEPS:
        state = step_states.get(key, "waiting")
        rows.append(
            f"""
            <div class="if-agent-row {state}">
                <div class="if-agent-info">
                    <div class="if-agent-name">{name} Agent</div>
                    <div class="if-agent-desc">{html.escape(desc)}</div>
                </div>
                <div class="if-status-pill {state}">{icon[state]} {label[state]}</div>
            </div>
            """
        )
    _md(f'<div class="if-panel">{"".join(rows)}</div>')


def render_progress_bar(done: int, total: int):
    pct = 0 if total == 0 else round(100 * done / total)
    _md(
        f"""
        <div class="if-progress-track">
            <div class="if-progress-fill" style="width:{pct}%;"></div>
        </div>
        """
    )


def render_metrics(metrics: dict):
    """
    metrics: {"relevance": 0-100|None, "quality": 0-10|None,
              "latency": seconds|None, "sources": int|None}
    Thresholds follow the synopsis's own success metrics.
    """

    def cls(val, good_min, warn_min):
        if val is None:
            return ""
        if val >= good_min:
            return "good"
        if val >= warn_min:
            return "warn"
        return "bad"

    rel = metrics.get("relevance")
    qual = metrics.get("quality")
    lat = metrics.get("latency")
    src = metrics.get("sources")
    lat_cls = "" if lat is None else ("good" if lat <= 60 else "bad")

    cards = [
        ("Source Relevance", f"{rel:.0f}%" if rel is not None else "—", "target ≥ 85%", cls(rel, 85, 70)),
        ("Report Quality", f"{qual:.1f}/10" if qual is not None else "—", "target ≥ 8.0", cls(qual, 8, 6)),
        ("Latency", f"{lat:.0f}s" if lat is not None else "—", "target ≤ 60s", lat_cls),
        ("Verified Sources", f"{src}" if src is not None else "—", "target ≥ 5", ""),
    ]
    parts = [
        f"""
        <div class="if-metric">
            <div class="if-metric-label">{label}</div>
            <div class="if-metric-value {c}">{value}</div>
            <div class="if-metric-target">{target}</div>
        </div>
        """
        for label, value, target, c in cards
    ]
    _md(f'<div class="if-metrics">{"".join(parts)}</div>')


def render_panel(title: str, body_html: str, accent: str = "signal"):
    """Single-call panel — see the note in _md() for why this matters."""
    _md(
        f'<div class="if-panel"><div class="if-panel-head">'
        f'<span class="accent-{accent}">{title}</span></div>{body_html}</div>'
    )


def render_subtopics(subtopics: list[str]):
    rows = "".join(
        f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(s)}</div>'
        for s in subtopics
    ) or '<div class="if-row">No subtopics generated.</div>'
    render_panel("Planner — Subtopics", rows, "signal")


def render_sources(sources: list[dict]):
    """sources: [{"title": str, "url": str, "source_type": "web"|"rag"}]"""
    if not sources:
        body = '<div class="if-row">No sources retrieved yet.</div>'
    else:
        parts = []
        for s in sources:
            tag_cls = "rag" if s.get("source_type") == "rag" else "web"
            tag_label = "RAG" if s.get("source_type") == "rag" else "WEB"
            url = s.get("url", "")
            title = html.escape(s.get("title", "Untitled"))
            # FIX (#1): previously this was a plain <div> holding the
            # URL as text — never clickable. Now it's a real <a> tag
            # that opens the source in a new tab.
            # FIX (#2): added a `title` attribute so hovering over a
            # truncated URL (see styles.css .if-source-url) shows the
            # full link as a native tooltip.
            url_html = (
                f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer" '
                f'class="if-source-url" title="{html.escape(url)}">{html.escape(url)}</a>'
                if url else '<div class="if-source-url">No URL available</div>'
            )
            parts.append(
                f"""
                <div class="if-source">
                    <span class="if-tag {tag_cls}">{tag_label}</span>
                    <div class="if-source-body">
                        <div class="if-source-title">{title}</div>
                        {url_html}
                    </div>
                </div>
                """
            )
        body = "".join(parts)
    render_panel("Research — Retrieved Sources", body, "signal")


def render_verification(verified_sources: list[dict], conflicts: list[str]):
    """verified_sources: [{"title","url","trust_score":0-100,"status":"verified"|"conflict"|"unverified"}]"""
    color_map = {"verified": "var(--signal)", "conflict": "var(--alert)", "unverified": "var(--text-faint)"}
    parts = []
    for s in verified_sources:
        status = s.get("status", "unverified")
        score = s.get("trust_score", 0)
        bar_color = color_map.get(status, "var(--text-faint)")
        url = s.get("url", "")
        title = html.escape(s.get("title", "Untitled"))
        # FIX (#1) + FIX (#2): same as render_sources — clickable link,
        # plus a title attribute for the full-URL tooltip on hover.
        url_html = (
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer" '
            f'class="if-source-url" title="{html.escape(url)}">{html.escape(url)}</a>'
            if url else '<div class="if-source-url">No URL available</div>'
        )
        parts.append(
            f"""
            <div class="if-source">
                <div class="if-trust-bar-track">
                    <div class="if-trust-bar-fill" style="width:{score}%;background:{bar_color};"></div>
                </div>
                <div class="if-source-body">
                    <div class="if-source-title">{title}</div>
                    {url_html}
                </div>
                <span class="if-trust-tag {status}">{score:.0f}%</span>
            </div>
            """
        )
    if conflicts:
        parts.append('<div style="height:0.6rem;"></div>')
        for c in conflicts:
            parts.append(
                f'<div class="if-row"><span class="if-row-marker" style="color:var(--alert);">⚠</span>{html.escape(c)}</div>'
            )
    render_panel("Verification — Trust Ledger", "".join(parts), "signal")


def render_analysis(insights: list[str], trends: list[str], risks: list[str], recommendations: list[str]):
    parts = []
    for label, items in [("Trends", trends), ("Risks", risks), ("Insights", insights), ("Recommendations", recommendations)]:
        if not items:
            continue
        parts.append(f'<div class="if-section-label" style="color:var(--insight);">{label}</div>')
        parts.append("".join(f'<div class="if-row"><span class="if-row-marker">·</span>{html.escape(i)}</div>' for i in items))
    render_panel("Analysis — Insights & Risk", "".join(parts), "insight")


def render_text_panel(title: str, text: str, accent: str = "signal"):
    """For prose sections like Executive Summary. Splits on blank lines
    into paragraphs, escapes each, and builds the whole card as one
    string — see the note in _md() for why splitting this across
    multiple calls would break the card's visual nesting."""
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    body = "".join(f'<p class="if-report-text">{html.escape(p)}</p>' for p in paragraphs)
    render_panel(title, body or '<div class="if-row">Nothing here yet.</div>', accent)


def render_numbered_list(title: str, items: list[str], accent: str = "signal"):
    rows = "".join(
        f'<div class="if-row"><span class="if-row-marker">{i}.</span>{html.escape(x)}</div>'
        for i, x in enumerate(items, 1)
    ) or '<div class="if-row">Nothing here yet.</div>'
    render_panel(title, rows, accent)


def render_arrow_list(title: str, items: list[str], accent: str = "insight"):
    rows = "".join(
        f'<div class="if-row"><span class="if-row-marker">→</span>{html.escape(x)}</div>'
        for x in items
    ) or '<div class="if-row">Nothing here yet.</div>'
    render_panel(title, rows, accent)


def render_concepts(items: list[str], title: str = "Important Concepts"):
    chips = "".join(f'<span class="if-tag concept">{html.escape(c)}</span>' for c in items)
    render_panel(title, chips or '<div class="if-row">No concepts extracted.</div>', "insight")


def render_swot(strengths: list[str], weaknesses: list[str]):
    s_rows = "".join(
        f'<div class="if-row"><span class="if-row-marker" style="color:var(--signal);">+</span>{html.escape(s)}</div>'
        for s in strengths
    ) or '<div class="if-row">None noted.</div>'
    w_rows = "".join(
        f'<div class="if-row"><span class="if-row-marker" style="color:var(--alert);">–</span>{html.escape(w)}</div>'
        for w in weaknesses
    ) or '<div class="if-row">None noted.</div>'
    body = (
        f'<div class="if-swot-grid">'
        f'<div><div class="if-section-label" style="color:var(--signal);">Strengths</div>{s_rows}</div>'
        f'<div><div class="if-section-label" style="color:var(--alert);">Weaknesses</div>{w_rows}</div>'
        f'</div>'
    )
    render_panel("Strengths &amp; Weaknesses", body, "review")


def render_footer():
    _md('<div class="if-footer">AgentHive · LangGraph multi-agent pipeline · ChromaDB RAG · Streamlit</div>')