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

        # Attempt 1: direct parse
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Attempt 2: extract the first {...} block in case of extra text around it
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Attempt 3: response got cut off mid-JSON (common when max_tokens is too
        # low for large research results) — try to salvage it by trimming back
        # to the last complete object/array and auto-closing open brackets.
        salvaged = self._try_salvage_truncated_json(cleaned)
        if salvaged is not None:
            print("DEBUG: VERIFICATION JSON WAS TRUNCATED — salvage succeeded.")
            return salvaged

        # Nothing worked — log details so it's easy to confirm truncation
        # from the console instead of silently returning an empty result.
        print("DEBUG: VERIFICATION PARSE FAILED. RAW LENGTH:", len(raw_content))
        print("DEBUG: RAW TAIL (last 300 chars):", raw_content[-300:])

        return {
            "error": "Failed to parse verification output",
            "raw_response": raw_content
        }

    def _try_salvage_truncated_json(self, text):
        """
        If the model's response was cut off before finishing the JSON
        (e.g. hit max_tokens mid-object), this trims trailing partial
        content and closes any open brackets/braces so we can still
        parse whatever complete data we did get, instead of losing
        the entire response.
        """
        # Cut back to the last place a value cleanly ended.
        last_good = max(text.rfind("}"), text.rfind("]"))
        if last_good == -1:
            return None
        trimmed = text[: last_good + 1]

        # Balance any unclosed braces/brackets that remain.
        open_braces = trimmed.count("{") - trimmed.count("}")
        open_brackets = trimmed.count("[") - trimmed.count("]")
        trimmed += "}" * max(open_braces, 0)
        trimmed += "]" * max(open_brackets, 0)

        try:
            return json.loads(trimmed)
        except Exception:
            return None