import json
import re

from agents.prompts import RESEARCH_PROMPT
from tools.web_search import web_search


class ResearchAgent:

    def __init__(self, model):
        self.model = model
        self.chain = RESEARCH_PROMPT | model

    def research(self, query, goal, tasks):
        """
        Perform research using Tavily search results
        and return structured JSON output.
        """
        # Limit to first 4 tasks to keep the prompt/response size manageable
        # and avoid truncation on smaller max_tokens budgets.
        tasks = tasks[:4]

        search_data = []

        for task in tasks:
            try:
                results = web_search(task, max_results=2)
                search_data.append({
                    "task": task,
                    "search_results": results
                })
            except Exception as e:
                search_data.append({
                    "task": task,
                    "search_results": [],
                    "error": str(e)
                })

        response = None
        try:
            response = self.chain.invoke(
                {
                    "query": query,
                    "goal": goal,
                    "tasks": json.dumps(search_data, indent=2)
                }
            )
            return self._parse_response(response.content)
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

        # Fallback: extract the first {...} block in case of extra text
        # or a truncated tail after valid JSON.
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