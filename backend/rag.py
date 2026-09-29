"""
rag.py
------
This script handles the Retrieval-Augmented Generation (RAG) pipeline.
It is responsible for loading SACCO policy documents, chunking the text,
generating vector embeddings using a local open-source model, 
and storing them in a local vector database (ChromaDB).
It also exposes a function to retrieve relevant document chunks based on a user query.
"""

import os
from dotenv import load_dotenv

# LangChain document loaders and text splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Local open-source embeddings and Chroma vector store
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables from the .env file in the root directory.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Define the directory where our policy PDFs are stored.
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policies")

# Define the directory where ChromaDB will persist its data locally.
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def initialize_vector_store():
    """
    Loads PDFs from the data directory, splits them into chunks,
    generates embeddings using a local Hugging Face model, and stores them in ChromaDB.
    Returns the Chroma vector store object.
    """
    print("Initializing RAG pipeline with local Hugging Face embeddings...")
    
    # 1. Load all PDF files from the data/policies directory
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {DATA_DIR}. Please add policy documents.")
    
    all_documents = []
    for pdf_file in pdf_files:
        file_path = os.path.join(DATA_DIR, pdf_file)
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        # Add metadata to track which file the chunk came from
        for doc in documents:
            doc.metadata["source"] = pdf_file
        all_documents.extend(documents)
    
    print(f"Loaded {len(all_documents)} pages from {len(pdf_files)} PDF(s).")

    # 2. Split the documents into smaller chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # 3. Initialize the local Hugging Face Embedding model.
    # 'all-MiniLM-L6-v2' is a fast, lightweight, and highly effective open-source model.
    # It runs entirely on your local machine, ensuring data privacy.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create or load the ChromaDB vector store.
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    # Persist the database to disk to save memory and loading time on subsequent runs.
    vector_store.persist()
    print(f"Vector store initialized and persisted to {CHROMA_PERSIST_DIR}.")
    
    return vector_store

def get_retriever(vector_store):
    """
    Converts the vector store into a retriever object.
    The retriever is what the AI Agent will use as a 'Tool' to fetch information.
    """
    # k=3 means it will return the top 3 most relevant document chunks for any query.
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return retriever

def test_retrieval():
    """
    A simple test function to verify the RAG pipeline is working correctly.
    It queries the vector store with a sample question and prints the retrieved chunks.
    """
    print("\n--- Testing RAG Retrieval ---")
    
    # Initialize the store using the same local Hugging Face embeddings.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    
    retriever = get_retriever(vector_store)
    
    # Simulate a user question.
    test_query = "What is the maximum loan amount a member can get?"
    print(f"Query: {test_query}")
    
    # Fetch relevant documents.
    relevant_docs = retriever.invoke(test_query)
    
    print(f"Retrieved {len(relevant_docs)} relevant chunks:\n")
    for i, doc in enumerate(relevant_docs):
        print(f"--- Chunk {i+1} (Source: {doc.metadata.get('source', 'Unknown')}) ---")
        # Print the first 200 characters of the chunk to verify content.
        print(doc.page_content[:200].replace('\n', ' '))
        print("...\n")

if __name__ == "__main__":
    # Run the initialization and test if this script is executed directly.
    initialize_vector_store()
    test_retrieval()