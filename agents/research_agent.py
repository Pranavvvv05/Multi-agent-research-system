import json
import re

from agents.prompts import RESEARCH_PROMPT
from tools.web_search import web_search
from rag.retrieval import retrieve_for_task


class ResearchAgent:

    def __init__(self, model):
        self.model = model
        self.chain = RESEARCH_PROMPT | model

    def research(self, query, goal, tasks, retriever=None):
        """
        Perform research using Tavily search results (+ knowledge-base chunks
        from the RAG retriever, if one is given) and return structured JSON output.
        """
        tasks = tasks[:4]
        search_data = []

        for task in tasks:
            # Handle if task is passed as a dict or raw string
            task_str = task.get("task", str(task)) if isinstance(task, dict) else str(task)

            try:
                results = web_search(task_str, max_results=2)
                entry = {
                    "task": task_str,
                    "search_results": results
                }
            except Exception as e:
                entry = {
                    "task": task_str,
                    "search_results": [],
                    "error": str(e)
                }

            # RAG: uploaded document ke relevant chunks retrieve karo
            kb = retrieve_for_task(retriever, task_str) if retriever else []
            if kb:
                entry["knowledge_base_results"] = kb

            search_data.append(entry)

        response = None
        try:
            response = self.chain.invoke(
                {
                    "query": query,
                    "goal": goal,
                    "tasks": json.dumps(search_data, indent=2)
                }
            )
            parsed = self._parse_response(response.content)

            # Safeguard: LLM agar sources me kb:// link bhool jaye toh inject kar do taaki UI me RAG tag dikhe
            if isinstance(parsed, dict) and "research_results" in parsed:
                for idx, t in enumerate(parsed["research_results"]):
                    if idx < len(search_data) and search_data[idx].get("knowledge_base_results"):
                        sources = t.setdefault("sources", [])
                        if not any(str(s).startswith("kb://") for s in sources):
                            # Default knowledge-base reference
                            sources.append(f"kb://document-chunk-{idx + 1}")

            return parsed
        except Exception as e:
            return {
                "error": "Failed to parse research output",
                "exception": str(e),
                "raw_response": getattr(response, "content", None),
            }

    def _parse_response(self, raw_content):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Fallback: extract the first {...} block
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        return {
            "error": "Failed to parse research output",
            "raw_response": raw_content
        }