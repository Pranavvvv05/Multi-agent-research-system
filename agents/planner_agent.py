import json
import re

from agents.prompts import PLANNER_PROMPT


def _to_text(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for k in ("title", "subtopic", "name", "description"):
            if item.get(k):
                return str(item[k])
        return " - ".join(str(v) for v in item.values())
    return str(item)


class PlannerAgent:

    def __init__(self, model):
        self.model = model
        self.chain = PLANNER_PROMPT | model

    def plan(self, query):
        """
        Generate a structured research plan from the user query.
        """
        response = None
        try:
            response = self.chain.invoke(
                {
                    "query": query
                }
            )

            response_text = response.content.strip()

            # Remove markdown code fences if present
            response_text = re.sub(
                r"^```json\s*",
                "",
                response_text
            )

            response_text = re.sub(
                r"\s*```$",
                "",
                response_text
            )

            plan = json.loads(response_text)

            # Normalize: smaller models sometimes return subtopics as dicts
            if isinstance(plan, dict) and isinstance(plan.get("subtopics"), list):
                plan["subtopics"] = [_to_text(s) for s in plan["subtopics"]]

            return plan

        except Exception as e:
            return {
                "error": "Failed to parse planner output",
                "exception": str(e),
                "raw_response": getattr(response, "content", None),
            }