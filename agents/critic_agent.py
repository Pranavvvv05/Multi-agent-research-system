import json
import re

from agents.prompts import CRITIC_PROMPT


class CriticAgent:

    def __init__(self, model):
        self.model = model
        self.chain = CRITIC_PROMPT | model

    def review(self, report):
        """
        Review final report and return structured JSON output.
        """

        response = self.chain.invoke(
            {
                "report": report
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
                "error": "Failed to parse critic output",
                "exception": str(e),
                "raw_response": response.content
            }