import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def ingest_knowledge_base():
    data_dir = os.path.join(BASE_DIR, "data")
    persist_directory = os.path.join(BASE_DIR, "chroma_db")

    print("1. Loading all PDFs...")
    documents = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_dir, filename)
            loader = PyMuPDFLoader(pdf_path)
            documents.extend(loader.load())
            print(f"Loaded {filename}")

    if not documents:
        print("Error: Could not find any PDFs in the data folder.")
        return
    print(f"Loaded {len(documents)} pages.")

    print("2. Chunking text...")
   
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)[:40]
    print(f"Created {len(chunks)} chunks.")

    print("3. Generating embeddings and storing in Vector DB (Chroma)...")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=persist_directory
    )
    
    print("Ingestion complete! Vector database saved to ./chroma_db")

if __name__ == "__main__":
    ingest_knowledge_base()