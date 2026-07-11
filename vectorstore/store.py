from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")

def store_chunks(chunks):
    """chunks:list of Document oobject (from ingest.py)
    stores chunk + embedding into ChormaDB, returns the vector store 
    """
    vector_store= Chroma.from_documents(
        documents=chunks,
        embedding=model,
        persist_directory="Chroma-db"
    )
    return vector_store
def get_retriever(vector_store):
    """
    Returns a retriever from the vector store for querying later
    """
    return vector_store.as_retriever()


if __name__ == "__main__":
    from langchain_core.documents import Document

    # Quick test with dummy data
    docs = [
        Document(page_content="Python is widely used in Artificial Intelligence.", metadata={"source": "AI_book"}),
        Document(page_content="Pandas is used for data analysis in Python.", metadata={"source": "DataScience_book"}),
        Document(page_content="Neural networks are used in deep learning.", metadata={"source": "DL_book"}),
    ]

    vector_store = store_chunks(docs)

    result = vector_store.similarity_search("What is used for data analysis?", k=2)
    for r in result:
        print(r.page_content)
        print(r.metadata)

    retriever = get_retriever(vector_store)
    retrieved_docs = retriever.invoke("Explain deep learning")

    for d in retrieved_docs:
        print(d)