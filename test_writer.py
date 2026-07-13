from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

from agents.writer_agent import WriterAgent

load_dotenv()

model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

writer_agent = WriterAgent(model)

sample_analysis_results = {
    "analysis_results": [
        {
            "task": "AI Trends",

            "key_insights": [
                "AI adoption is accelerating across industries."
            ],

            "trends": [
                "Rapid growth in Generative AI."
            ],

            "risks": [
                "Market projections may be overestimated."
            ],

            "opportunities": [
                "Expansion into new industries."
            ],

            "recommendations": [
                "Monitor AI investment trends."
            ]
        }
    ],

    "overall_summary": [
        "AI adoption continues to grow globally."
    ]
}

sources = [
    "https://www.ibm.com",
    "https://www.mckinsey.com"
]

report = writer_agent.write_report(
    analysis_results=sample_analysis_results,
    sources=sources
)

print(report)