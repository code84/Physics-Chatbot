from langchain_experimental.text_splitter import SemanticChunker
import os
import shutil
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, BSHTMLLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

def build_vector_database():
    """
    Phase 1: Ingests documents with a Dev Mode toggle for rapid prototyping.
    """
    raw_data_path = "../data/raw"
    db_path = "../data/physics_db"
    
   
    DEV_MODE = True
    DEV_LIMIT = 20 

    
    if os.path.exists(db_path):
        print("🗑️ Deleting interrupted database files...")
        shutil.rmtree(db_path)
    
    print("\n1. Loading textbooks from data/raw...")
    
    pdf_loader = DirectoryLoader(raw_data_path, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True)
    pdf_docs = pdf_loader.load()
    
    html_loader = DirectoryLoader(raw_data_path, glob="**/*.html", loader_cls=BSHTMLLoader, loader_kwargs={"open_encoding": "utf-8"}, show_progress=True)
    html_docs = html_loader.load()
    
    documents = pdf_docs + html_docs
    
    if not documents:
        print("Error: No physics files found.")
        return

    # --- THE DEV MODE SLICER ---
    if DEV_MODE:
        print(f"\n⚠️ DEV MODE ACTIVE: Shrinking dataset from {len(documents)} down to {DEV_LIMIT} chapters for rapid testing.")
        documents = documents[:DEV_LIMIT]
    else:
        print(f"\n🚀 PROD MODE ACTIVE: Processing all {len(documents)} chapters.")

    print("\n2. Chunking text using AI Semantic Chunking...")
    
    # THE UPGRADE: The chunker  uses AI to read sentence meaning before cutting
    text_splitter = SemanticChunker(OllamaEmbeddings(model="nomic-embed-text"))
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} meaning-based chunks.")
    print("\n3. Initializing local Ollama Embedding Model...")
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")

    print("\n4. Generating embeddings and building Chroma Vector DB...")
    vector_db = Chroma(embedding_function=embedding_model, persist_directory=db_path)
    
    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding Progress", unit="batch"):
        batch = chunks[i:i+batch_size]
        vector_db.add_documents(batch)
        
    print(f"\n✅ Success! Phase 1 complete. Mini-DB saved to {db_path}")

if __name__ == "__main__":
    build_vector_database()