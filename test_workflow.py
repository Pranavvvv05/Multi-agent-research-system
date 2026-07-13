from dotenv import load_dotenv
load_dotenv()

from graph.workflow import workflow

if __name__ == "__main__":
    query = input("Enter your research query: ")
    result = workflow.invoke({"query": query})

    print("\n\n===== FINAL REPORT =====\n")
    print(result["report"])

    print("\n\n===== CRITIC REVIEW =====\n")
    print(result["critic_review"])