from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

from agents.analysis_agent import AnalysisAgent

load_dotenv()

model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

analysis_agent = AnalysisAgent(model)

sample_verified_results = {
    "verified_results": [
        {
            "task": "AI Trends",

            "verified_findings": [
                {
                    "claim": "AI adoption is increasing across industries.",
                    "verification_status": "verified",
                    "confidence_score": 0.95
                },
                {
                    "claim": "Generative AI investments are growing rapidly.",
                    "verification_status": "verified",
                    "confidence_score": 0.94
                },
                {
                    "claim": "AI market expected to exceed $1 trillion by 2030.",
                    "verification_status": "partially_verified",
                    "confidence_score": 0.75
                }
            ],

            "overall_task_confidence": 0.92
        }
    ]
}

result = analysis_agent.analyze(
    sample_verified_results
)

print(result)