from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_mistralai import ChatMistralAI
from vectorstore.store import get_vector_store


def get_retriever(vector_store):
    choice = input("Enter retrieval method (similarity/mmr/multiquery): ").strip().lower()

    if choice == "similarity":
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

    elif choice == "mmr":
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3}
        )

    elif choice == "multiquery":
        llm = ChatMistralAI(model="mistral-small-latest")
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

    else:
        print("Invalid choice! Use similarity/mmr/multiquery.")
        return None

    return retriever


if __name__ == "__main__":
    vector_store = get_vector_store()
    retriever = get_retriever(vector_store)

    if retriever:
        query = input("Enter your question: ").strip()
        results = retriever.invoke(query)

        print("\n===== Results =====\n")
        for doc in results:
            print(doc.page_content)