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
        response = None
        try:
            response = self.chain.invoke(
                {
                    "verified_results": json.dumps(verified_results, indent=2)
                }
            )
            return self._parse_response(response.content)
        except Exception as e:
            return {
                "error": "Failed to parse analysis output",
                "exception": str(e),
                "raw_response": getattr(response, "content", None),
            }

    def _parse_response(self, raw_content):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        return {
            "error": "Failed to parse analysis output",
            "raw_response": raw_content
        }