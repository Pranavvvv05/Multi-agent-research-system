import os
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_mistralai import ChatMistralAI

from agents.planner_agent import PlannerAgent
from agents.research_agent import ResearchAgent
from agents.verification_agent import VerificationAgent
from agents.analysis_agent import AnalysisAgent
from agents.writer_agent import WriterAgent
from agents.critic_agent import CriticAgent


class ResearchState(TypedDict):
    query: str
    plan: Dict[str, Any]
    research_results: Dict[str, Any]
    verified_results: Dict[str, Any]
    analysis_results: Dict[str, Any]
    sources: List[Dict[str, str]]
    report: str
    critic_review: Dict[str, Any]

model = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    timeout=180,
    max_retries=2,
    max_tokens=4000,
)

planner = PlannerAgent(model)
researcher = ResearchAgent(model)
verifier = VerificationAgent(model)
analyst = AnalysisAgent(model)
writer_agent = WriterAgent(model)
critic_agent = CriticAgent(model)


def planner_node(state: ResearchState) -> ResearchState:
    state["plan"] = planner.plan(state["query"])
    return state


def research_node(state: ResearchState) -> ResearchState:
    plan = state["plan"]
    state["research_results"] = researcher.research(
        state["query"], plan.get("goal", ""), plan.get("tasks", [])
    )
    return state


def verification_node(state: ResearchState) -> ResearchState:
    state["verified_results"] = verifier.verify(state["research_results"])
    return state


def analysis_node(state: ResearchState) -> ResearchState:
    state["analysis_results"] = analyst.analyze(state["verified_results"])
    return state


def extract_sources(verified_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Returns a deduplicated, alphabetically sorted list of
    {"title": ..., "url": ...} dicts built from verified sources.
    """
    seen = {}
    for task in verified_results.get("verified_results", []):
        task_name = task.get("task", "Source")
        for src in task.get("verified_sources", []):
            url = src.get("source")
            if url and url not in seen:
                seen[url] = task_name

    return sorted(
        [{"title": title, "url": url} for url, title in seen.items()],
        key=lambda x: x["title"]
    )


def build_sources_markdown(sources: List[Dict[str, str]]) -> str:
    """Generates a clean, ordered, clickable Sources section as markdown."""
    if not sources:
        return "\n## Sources\nNo verified sources available.\n"
    lines = ["\n## Sources"]
    for i, s in enumerate(sources, 1):
        lines.append(f"{i}. [{s['title']}]({s['url']})")
    return "\n".join(lines)


def writer_node(state: ResearchState) -> ResearchState:
    state["sources"] = extract_sources(state["verified_results"])
    raw_report = writer_agent.write_report(state["analysis_results"], state["sources"])
    sources_section = build_sources_markdown(state["sources"])
    state["report"] = f"{raw_report}\n{sources_section}"
    return state


def critic_node(state: ResearchState) -> ResearchState:
    state["critic_review"] = critic_agent.review(state["report"])
    return state


graph = StateGraph(ResearchState)

graph.add_node("planner", planner_node)
graph.add_node("research", research_node)
graph.add_node("verification", verification_node)
graph.add_node("analysis", analysis_node)
graph.add_node("writer", writer_node)
graph.add_node("critic", critic_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "research")
graph.add_edge("research", "verification")
graph.add_edge("verification", "analysis")
graph.add_edge("analysis", "writer")
graph.add_edge("writer", "critic")
graph.add_edge("critic", END)

workflow = graph.compile()


def run_pipeline(document_text: str, use_rag: bool = True):
    """
    Generator required by app.py. Runs each agent in sequence
    and yields (step_key, payload) after every step finishes, mapped
    to the exact shape the UI expects.
    """
    state: ResearchState = {
        "query": document_text,
        "plan": {}, "research_results": {}, "verified_results": {},
        "analysis_results": {}, "sources": [], "report": "", "critic_review": {},
    }

    # ── Planner ──────────────────────────────────────────────
    state = planner_node(state)
    plan = state["plan"]
    print("DEBUG RAW PLAN:", plan)  # 👈 DEBUG
    subtopics = plan.get("tasks") or []
    yield "planner", {"subtopics": subtopics}

    # ── Research ─────────────────────────────────────────────
    state = research_node(state)
    print("DEBUG RAW RESEARCH RESULTS:", state["research_results"])  # 👈 DEBUG
    research_tasks = state["research_results"].get("research_results") or []
    raw_sources = []
    for task in research_tasks:
        for url in task.get("sources", []):
            raw_sources.append({
                "title": task.get("task", "Untitled"),
                "url": url,
                "source_type": "web",
            })
    yield "research", {"sources": raw_sources}

    # ── Verification ─────────────────────────────────────────
    state = verification_node(state)
    print("DEBUG RAW VERIFIED RESULTS:", state["verified_results"])  # 👈 DEBUG
    verified_tasks = state["verified_results"].get("verified_results") or []
    verified_sources = []
    conflicts = []
    quality_to_score = {"high": 90, "medium": 65, "low": 30}

    total_sources = 0
    relevant_sources = 0

    for task in verified_tasks:
        for vs in task.get("verified_sources", []):
            quality = vs.get("source_quality", "medium")
            total_sources += 1
            if quality in ("high", "medium"):
                relevant_sources += 1
            verified_sources.append({
                "title": task.get("task", "Untitled"),
                "url": vs.get("source", ""),
                "trust_score": quality_to_score.get(quality, 50),
                "status": "unverified" if quality == "low" else "verified",
            })
        for c in task.get("conflicting_information", []):
            conflicts.append(c.get("claim", str(c)) if isinstance(c, dict) else str(c))

    source_relevance = round((relevant_sources / total_sources) * 100, 1) if total_sources else 0

    yield "verification", {
        "verified_sources": verified_sources,
        "conflicts": conflicts,
        "source_relevance": source_relevance,
        "relevance_score": source_relevance,
    }

    # ── Analysis ─────────────────────────────────────────────
    state = analysis_node(state)
    print("DEBUG RAW ANALYSIS RESULTS:", state["analysis_results"])  # 👈 DEBUG
    analysis_tasks = state["analysis_results"].get("analysis_results") or []
    insights, trends, risks, opportunities, recommendations_analysis = [], [], [], [], []
    for task in analysis_tasks:
        insights.extend(task.get("key_insights", []))
        trends.extend(task.get("trends", []))
        risks.extend(task.get("risks", []))
        opportunities.extend(task.get("opportunities", []))
        recommendations_analysis.extend(task.get("recommendations", []))
    yield "analysis", {
        "insights": insights,
        "trends": trends,
        "risks": risks,
        "recommendations": recommendations_analysis,
    }

    # ── Writer ───────────────────────────────────────────────
    state = writer_node(state)
    report_text = state["report"] if isinstance(state["report"], str) else ""

    yield "writer", {
        "executive_summary": report_text,
        "report_markdown": report_text,
        "key_findings": insights,
        "important_concepts": trends,
        "strengths": opportunities,
        "weaknesses": risks,
        "recommendations": recommendations_analysis,
    }

    # ── Critic ───────────────────────────────────────────────
    state = critic_node(state)
    c = state["critic_review"]
    yield "critic", {
        "score": c.get("overall_score", 0),
        "feedback": "; ".join(c.get("issues", [])) or c.get("review_status", ""),
        "strengths": c.get("strengths", []),
        "improvements": c.get("improvement_suggestions", []),
    }