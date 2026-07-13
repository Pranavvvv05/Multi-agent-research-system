import json
import re

from agents.prompts import PLANNER_PROMPT


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

            return json.loads(response_text)

        except Exception as e:
            return {
                "error": "Failed to parse planner output",
                "exception": str(e),
                "raw_response": getattr(response, "content", None),
            }