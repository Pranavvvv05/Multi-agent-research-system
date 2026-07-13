import json
import re

from agents.prompts import ANALYSIS_PROMPT


class AnalysisAgent:

    def __init__(self, model):
        self.model = model
        self.chain = ANALYSIS_PROMPT | model

    def analyze(self, verified_results):
        """
        Analyze verified findings and return structured JSON output.
        """

        response = self.chain.invoke(
            {
                "verified_results": json.dumps(
                    verified_results,
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
                "error": "Failed to parse analysis output",
                "exception": str(e),
                "raw_response": response.content
            }