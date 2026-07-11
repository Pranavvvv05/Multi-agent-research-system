import json
import re
from agents.prompts import VERIFICATION_PROMPT


class VerificationAgent:
    def __init__(self, model):
        self.model = model
        self.chain = VERIFICATION_PROMPT | model

    def verify(self, research_results):
        """
        Verify research findings and return structured JSON output.
        """
        response = self.chain.invoke(
            {
                "research_results": json.dumps(
                    research_results,
                    indent=2
                )
            }
        )
        return self._parse_response(response.content)

    def _parse_response(self, raw_content):
        # Strip markdown code fences (```json ... ``` or ``` ... ```) if present
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip())
        try:
            return json.loads(cleaned)
        except Exception:
            pass
        # Fallback: extract the first {...} block in case of extra text around it
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {
            "error": "Failed to parse verification output",
            "raw_response": raw_content
        }