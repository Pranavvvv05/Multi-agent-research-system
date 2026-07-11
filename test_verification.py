from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

from agents.verification_agent import VerificationAgent

load_dotenv()


model = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0
)

verification_agent = VerificationAgent(model)

sample_research_results = {
    "research_results": [
        {
            "task": "AI Trends",

            "findings": [
                "AI adoption is increasing across industries.",
                "Generative AI investments are growing rapidly."
            ],

            "sources": [
                "https://www.ibm.com",
                "https://www.mckinsey.com"
            ],

            "statistics": [
                "AI market expected to exceed $1 trillion by 2030."
            ]
        }
    ]
}

result = verification_agent.verify(
    sample_research_results
)

print(result)