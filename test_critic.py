from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

from agents.critic_agent import CriticAgent

load_dotenv()

model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

critic_agent = CriticAgent(model)

sample_report = """
# AI Trends Report

## Introduction
AI adoption is increasing across industries.

## Key Findings
Generative AI investments are growing rapidly.

## Analysis
Organizations are investing heavily in AI capabilities.

## Recommendations
Invest in AI training and infrastructure.

## Conclusion
AI will remain a major growth driver.

## Sources
https://www.ibm.com
https://www.mckinsey.com
"""

result = critic_agent.review(sample_report)

print(result)