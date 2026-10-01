"""
agent.py
--------
This script defines the core AI Agent for the SmartSACCO application.
The agent uses Google Gemini as its reasoning engine and is equipped with 
two distinct tools:
1. A REST API tool to fetch live member financial data.
2. A RAG tool to query official SACCO policy documents using local embeddings.
"""

import os
import requests
import streamlit as st  # Added to access Streamlit Cloud secrets
from dotenv import load_dotenv

# LangChain core components for agents and tools
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# Import classic agent components (required for LangChain 0.3.x)
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

# LangChain Google Generative AI integration for the LLM brain
from langchain_google_genai import ChatGoogleGenerativeAI

# Local imports for our RAG pipeline (using local embeddings for data privacy)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================================
# ENVIRONMENT VARIABLE HANDLER
# ==========================================

def get_env_var(var_name, default=None):
    """
    Fetches environment variables. Checks Streamlit Cloud secrets first,
    then falls back to standard OS environment variables.
    """
    try:
        # Check Streamlit Cloud secrets (for frontend deployment)
        if st.secrets.get(var_name):
            return st.secrets[var_name]
    except Exception:
        pass
    
    # Fallback to standard environment variables (for local/Render backend)
    return os.getenv(var_name, default)

# Force LangChain to use the correct API Key from Streamlit Secrets if available
google_api_key = get_env_var("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key

# Load local .env file as a final fallback for local development
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Define the path to the persisted ChromaDB vector store (must match rag.py)
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# ==========================================
# TOOL DEFINITIONS
# ==========================================

@tool
def get_member_financial_summary(member_id: str) -> str:
    """
    Fetches the financial summary (savings, outstanding loan, account status) 
    for a specific SACCO member using their member ID.
    Use this tool when the user asks about their account balance, 
    loan status, or provides their member ID (e.g., M001).
    """
    # Use the cloud-aware helper function to get the correct backend URL
    api_base_url = get_env_var("API_BASE_URL", "http://127.0.0.1:8000")
    url = f"{api_base_url}/api/members/{member_id}/financial-summary"
    
    try:
        # Added timeout=15 to prevent the app from hanging if the backend is asleep
        response = requests.get(url, timeout=15)
        
        # Handle the response based on the HTTP status code
        if response.status_code == 200:
            return str(response.json())
        elif response.status_code == 404:
            return "Error: Member not found. Please verify the member ID."
        else:
            return f"Error: API returned status code {response.status_code}."
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the backend API. Ensure the FastAPI server is running."
    except requests.exceptions.Timeout:
        return "Error: The backend API took too long to respond. It might be waking up from sleep."

@tool
def query_sacco_policy(query: str) -> str:
    """
    Searches the official SACCO policy documents for information regarding 
    rules, regulations, interest rates, and loan eligibility criteria.
    Use this tool when the user asks general questions about SACCO rules, 
    how to apply for a loan, or what the interest rates are.
    """
    try:
        # Initialize the local Hugging Face embedding model (matches rag.py)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load the existing local ChromaDB vector store from disk
        vector_store = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )
        
        # Convert the vector store into a retriever (fetches top 3 relevant chunks)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Perform the semantic search
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant policy information found in the documents."
        
        # Combine the retrieved text chunks into a single string for the LLM
        combined_docs = "\n\n".join([doc.page_content for doc in docs])
        return combined_docs
        
    except Exception as e:
        return f"Error querying the policy documents: {str(e)}"

# ==========================================
# AGENT INITIALIZATION
# ==========================================

def get_agent_executor():
    """
    Initializes the Google Gemini LLM, binds the tools to it, 
    and returns an AgentExecutor ready to process user queries.
    """
    # 1. Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest",
        temperature=0
    )
    
    # 2. Define the list of tools available to the agent
    tools = [get_member_financial_summary, query_sacco_policy]
    
    # 3. Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a helpful, professional, and accurate AI assistant for a SACCO. "
         "Use the provided tools to answer user questions. "
         "If a user asks about their specific account, you MUST use the financial summary tool. "
         "If a user asks about rules or rates, you MUST use the policy tool. "
         "If you cannot find the answer using the tools, politely state that you do not know. "
         "Do not make up information."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # 4. Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 5. Wrap in an AgentExecutor
    # Set verbose=False for cleaner UI output in production
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    
    return agent_executor

# ==========================================
# TESTING THE AGENT
# ==========================================

if __name__ == "__main__":
    print("Initializing SmartSACCO AI Agent...")
    executor = get_agent_executor()
    
    print("\n--- Test 1: RAG Tool (Policy Question) ---")
    test_query_1 = "What is the maximum loan amount a member can get?"
    response_1 = executor.invoke({"input": test_query_1})
    print(f"\nFinal Answer: {response_1['output']}\n")
    
    print("--- Test 2: REST API Tool (Account Question) ---")
    test_query_2 = "Can you check the savings balance for member M001?"
    response_2 = executor.invoke({"input": test_query_2})
    print(f"\nFinal Answer: {response_2['output']}\n")
    
    print("--- Test 3: Combined Tools (Complex Question) ---")
    test_query_3 = "I am member M002. Based on my current savings, am I eligible for a 100,000 KES loan?"
    response_3 = executor.invoke({"input": test_query_3})
    print(f"\nFinal Answer: {response_3['output']}\n")