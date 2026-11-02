import uuid
from functools import lru_cache

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


@lru_cache(maxsize=1)
def _embeddings():
    # lazy import: model tabhi load hoga jab RAG sach me use ho
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")


def build_retriever(text: str, source_name: str = "uploaded-document", k: int = 3):
    """Document ko chunk karke temporary in-memory Chroma me daalta hai."""
    from langchain_community.vectorstores import Chroma

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(
        [Document(page_content=text, metadata={"source": source_name})]
    )
    if not chunks:
        return None
    store = Chroma.from_documents(
        chunks,
        embedding=_embeddings(),
        collection_name=f"run_{uuid.uuid4().hex[:8]}",  # persist_directory nahi = in-memory
    )
    return store.as_retriever(search_type="mmr", search_kwargs={"k": k})


def retrieve_for_task(retriever, task: str, max_chars: int = 500) -> list[dict]:
    if retriever is None:
        return []
    try:
        docs = retriever.invoke(str(task))
    except Exception:
        return []
    return [
        {
            "title": d.metadata.get("source", "knowledge base"),
            "url": "kb://" + d.metadata.get("source", "document").replace(" ", "_"),
            "snippet": d.page_content[:max_chars],
        }
        for d in docs
    ]