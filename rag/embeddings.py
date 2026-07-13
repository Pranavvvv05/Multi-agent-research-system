from langchain_huggingface import HuggingFaceEmbeddings
model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")

def get_embeddings(chunks):
    """
    chunks: list of document objects(from ingest.py chunks)
    returns: list of embedding vectors
    """
    texts=[chunk.page_content for chunk in chunks]
    vectors= model.embed_documents(texts)
    return vectors

if __name__== "__main__":
    text = "This is a test sentence for embeddings."
    vector = model.embed_query(text)
    print(f"Vector length: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")