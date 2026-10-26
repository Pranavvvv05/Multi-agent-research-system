import json
import re
import time
import httpx
from agents.prompts import VERIFICATION_PROMPT

MAX_FIELD_CHARS = 800
MAX_ATTEMPTS = 5


def _shrink(obj):
    if isinstance(obj, str):
        return obj[:MAX_FIELD_CHARS]
    if isinstance(obj, list):
        return [_shrink(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _shrink(v) for k, v in obj.items()}
    return obj


class VerificationAgent:
    def __init__(self, model):
        self.model = model
        self.chain = VERIFICATION_PROMPT | model

    def verify(self, research_results):
        payload = {"research_results": json.dumps(_shrink(research_results))}
        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.chain.invoke(payload)
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < MAX_ATTEMPTS - 1:
                    time.sleep(20 * (attempt + 1))
                    continue
                raise
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