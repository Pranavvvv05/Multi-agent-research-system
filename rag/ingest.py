from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader,TextLoader,WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_document():
    choice= input("Enter source type (pdf/text/url): ").strip().lower()

    if choice == "pdf":
        path=input("Enter PDF file path : ").strip()
        loader=PyPDFLoader(path)
    elif choice == "text":
        path=input("Enter text file path: ").strip()
        loader=TextLoader(path,encoding="utf-8")
    elif choice=="url":
        url=input("Enter URL: ").strip()
        loader=WebBaseLoader(url)
    else:
        print("Invaild choice! Use pdf/text/url.")
        return[]
    return loader.load()

docs=load_document()

if docs:
    print(f"\nTotal document loaded: {len(docs)}\n")

    for i,doc in enumerate(docs):
        print(f"---Document {i+1}---")
        print(doc.page_content)
        print()
chunk_size = int(input("Enter chunk size (e.g. 1000): ").strip())
chunk_overlap = int(input("Enter chunk overlap (e.g. 150): ").strip())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)

chunks=splitter.split_documents(docs)
print(f"\nTotal chunks after splitting: {len(chunks)}") 