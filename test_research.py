from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

from agents.research_agent import ResearchAgent

load_dotenv()

model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

research_agent = ResearchAgent(model)

query = "Latest AI trends"

goal = "Understand current developments in AI"

tasks = [
    "AI adoption trends",
    "Generative AI growth",
    "Future of AI"
]

result = research_agent.research(
    query=query,
    goal=goal,
    tasks=tasks
)

print(result)