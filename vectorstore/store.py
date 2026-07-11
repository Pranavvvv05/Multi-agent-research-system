from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")


def store_chunks(chunks):
    """
    chunks: list of Document objects (from ingest.py)
    Stores chunks + embeddings into ChromaDB, returns the vector store
    """
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=model,
        persist_directory="Chroma-db"
    )
    return vector_store


def get_vector_store():
    """
    Loads the existing ChromaDB (already stored data)
    """
    return Chroma(
        persist_directory="Chroma-db",
        embedding_function=model
    )


if __name__ == "__main__":
    from langchain_core.documents import Document

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