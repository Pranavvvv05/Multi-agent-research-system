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

        search_data = []

        for task in tasks:
            try:
                results = web_search(task)

                search_data.append(
                    {
                        "task": task,
                        "search_results": results
                    }
                )

            except Exception as e:
                search_data.append(
                    {
                        "task": task,
                        "search_results": [],
                        "error": str(e)
                    }
                )

        response = self.chain.invoke(
            {
                "query": query,
                "goal": goal,
                "tasks": json.dumps(
                    search_data,
                    indent=2
                )
            }
        )

        try:
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
                "error": "Failed to parse research output",
                "exception": str(e),
                "raw_response": response.content
            }