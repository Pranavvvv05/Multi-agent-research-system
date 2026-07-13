import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.prompts import RESEARCH_PROMPT
from tools.web_search import web_search


class ResearchAgent:

    def __init__(self, model):
        self.model = model
        self.chain = RESEARCH_PROMPT | model

    def _search_one(self, task):
        try:
            results = web_search(task)
            print(f"[ResearchAgent] task='{task[:60]}...' → "
                  f"{len(results) if results else 0} results")
            return {"task": task, "search_results": results}
        except Exception as e:
            print(f"[ResearchAgent] ERROR on task '{task[:60]}...': {e}")
            return {"task": task, "search_results": [], "error": str(e)}

    def research(self, query, goal, tasks):
        """
        Perform research using web search results (in parallel)
        and return structured JSON output.
        """

        search_data = [None] * len(tasks)

        # Run all web_search calls concurrently instead of one-by-one
        with ThreadPoolExecutor(max_workers=min(10, len(tasks) or 1)) as executor:
            future_to_index = {
                executor.submit(self._search_one, task): i
                for i, task in enumerate(tasks)
            }
            for future in as_completed(future_to_index):
                i = future_to_index[future]
                search_data[i] = future.result()

        total_results = sum(len(d.get("search_results", [])) for d in search_data)
        print(f"[ResearchAgent] Total search results across all tasks: {total_results}")

        response = self.chain.invoke(
            {
                "query": query,
                "goal": goal,
                "tasks": json.dumps(search_data, indent=2)
            }
        )

        try:
            response_text = response.content.strip()
            response_text = re.sub(r"^```json\s*", "", response_text)
            response_text = re.sub(r"\s*```$", "", response_text)

            parsed = json.loads(response_text)
            result_count = len(parsed.get("research_results", []))
            source_count = sum(len(r.get("sources", [])) for r in parsed.get("research_results", []))
            print(f"[ResearchAgent] LLM returned {result_count} research_results, "
                  f"{source_count} total sources")
            return parsed

        except Exception as e:
            print(f"[ResearchAgent] JSON PARSE FAILED: {e}")
            return {
                "error": "Failed to parse research output",
                "exception": str(e),
                "raw_response": response.content
            }