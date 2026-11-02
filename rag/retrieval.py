import uuid
from functools import lru_cache
from typing import List, Dict, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


@lru_cache(maxsize=1)
def _embeddings():
    # lazy import: model tabhi load hoga jab RAG sach me use ho
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")


def build_retriever(text: str, source_name: str = "uploaded-document", k: int = 3):
    """Document ko chunk karke temporary in-memory Chroma me daalta hai."""
    if not text or not text.strip():
        return None

    from langchain_community.vectorstores import Chroma

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    raw_chunks = splitter.split_documents(
        [Document(page_content=text, metadata={"source": source_name})]
    )
    
    if not raw_chunks:
        return None

    # Har chunk ko unique index dena taaki URL unique bane
    chunks = []
    clean_src = source_name.replace(" ", "_")
    for i, doc in enumerate(raw_chunks, 1):
        doc.metadata["chunk_id"] = i
        doc.metadata["source_url"] = f"kb://{clean_src}#chunk-{i}"
        chunks.append(doc)

    store = Chroma.from_documents(
        chunks,
        embedding=_embeddings(),
        collection_name=f"run_{uuid.uuid4().hex[:8]}",  # in-memory collection
    )
    return store.as_retriever(search_type="mmr", search_kwargs={"k": k})


def retrieve_for_task(retriever, task: str, max_chars: int = 500) -> List[Dict[str, str]]:
    if retriever is None:
        return []
    try:
        docs = retriever.invoke(str(task))
    except Exception:
        return []

    return [
        {
            "title": f"{d.metadata.get('source', 'Knowledge Base')} (Chunk {d.metadata.get('chunk_id', 1)})",
            "url": d.metadata.get("source_url", "kb://uploaded-document"),
            "snippet": d.page_content[:max_chars],
        }
        for d in docs
    ]