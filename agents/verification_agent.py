import json
import re
import httpx
from agents.prompts import VERIFICATION_PROMPT


class VerificationAgent:
    def __init__(self, model):
        self.model = model
        self.chain = (VERIFICATION_PROMPT | model).with_retry(
            retry_if_exception_type=(httpx.HTTPStatusError,),
            stop_after_attempt=6,
            wait_exponential_jitter=True,
        )

    def verify(self, research_results):
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

        salvaged = self._try_salvage_truncated_json(cleaned)
        if salvaged is not None:
            print("DEBUG: VERIFICATION JSON WAS TRUNCATED — salvage succeeded.")
            return salvaged

        print("DEBUG: VERIFICATION PARSE FAILED. RAW LENGTH:", len(raw_content))
        print("DEBUG: RAW TAIL (last 300 chars):", raw_content[-300:])

        return {
            "error": "Failed to parse verification output",
            "raw_response": raw_content
        }

    def _try_salvage_truncated_json(self, text):
        last_good = max(text.rfind("}"), text.rfind("]"))
        if last_good == -1:
            return None
        trimmed = text[: last_good + 1]

        open_braces = trimmed.count("{") - trimmed.count("}")
        open_brackets = trimmed.count("[") - trimmed.count("]")
        trimmed += "}" * max(open_braces, 0)
        trimmed += "]" * max(open_brackets, 0)

        try:
            return json.loads(trimmed)
        except Exception:
            return None