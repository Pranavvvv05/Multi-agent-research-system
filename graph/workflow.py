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
    sources: List[str]
    report: str
    critic_review: Dict[str, Any]

model = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    timeout=60,
    max_retries=2,
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


def extract_sources(verified_results: Dict[str, Any]) -> List[str]:
    sources = set()
    for task in verified_results.get("verified_results", []):
        for src in task.get("verified_sources", []):
            if src.get("source"):
                sources.add(src["source"])
    return list(sources)


def writer_node(state: ResearchState) -> ResearchState:
    state["sources"] = extract_sources(state["verified_results"])
    state["report"] = writer_agent.write_report(state["analysis_results"], state["sources"])
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