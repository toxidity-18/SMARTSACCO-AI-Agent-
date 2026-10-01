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
from dotenv import load_dotenv

# LangChain core components for agents and tools
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

# Load environment variables (specifically the GOOGLE_API_KEY)
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
    # Construct the URL for our FastAPI backend endpoint
    url = f"http://127.0.0.1:8000/api/members/{member_id}/financial-summary"
    
    try:
        # Make the HTTP GET request to the REST API
        response = requests.get(url)
        
        # Handle the response based on the HTTP status code
        if response.status_code == 200:
            return str(response.json())
        elif response.status_code == 404:
            return "Error: Member not found. Please verify the member ID."
        else:
            return f"Error: API returned status code {response.status_code}."
            
    except requests.exceptions.ConnectionError:
        # This error occurs if the FastAPI server is not running
        return "Error: Could not connect to the backend API. Ensure the FastAPI server is running on port 8000."

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
    # We use 'models/gemini-flash-latest' as it is the stable, officially 
    # recommended alias that avoids experimental preview model bugs.
    # temperature=0 ensures deterministic, factual responses based on the tool outputs.
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest",
        temperature=0
    )
    
    # 2. Define the list of tools available to the agent
    tools = [get_member_financial_summary, query_sacco_policy]
    
    # 3. Create the prompt template
    # This guides the agent's behavior and persona.
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a helpful, professional, and accurate AI assistant for a SACCO. "
         "Use the provided tools to answer user questions. "
         "If a user asks about their specific account, you MUST use the financial summary tool. "
         "If a user asks about rules or rates, you MUST use the policy tool. "
         "If you cannot find the answer using the tools, politely state that you do not know. "
         "Do not make up information."),
        ("human", "{input}"),
        # The agent_scratchpad is where LangChain stores the LLM's internal reasoning 
        # and tool call results during the execution loop.
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # 4. Create the agent
    # This binds the LLM, the tools, and the prompt together.
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 5. Wrap in an AgentExecutor
    # The executor handles the loop: LLM thinks -> calls tool -> gets result -> LLM thinks again.
    # verbose=True prints the agent's internal reasoning to the terminal, which is great for debugging.
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

# ==========================================
# TESTING THE AGENT
# ==========================================

if __name__ == "__main__":
    print("Initializing SmartSACCO AI Agent...")
    executor = get_agent_executor()
    
    print("\n--- Test 1: RAG Tool (Policy Question) ---")
    # This question should trigger the query_sacco_policy tool
    test_query_1 = "What is the maximum loan amount a member can get?"
    response_1 = executor.invoke({"input": test_query_1})
    print(f"\nFinal Answer: {response_1['output']}\n")
    
    print("--- Test 2: REST API Tool (Account Question) ---")
    # This question should trigger the get_member_financial_summary tool
    # Note: The FastAPI server MUST be running for this to work.
    test_query_2 = "Can you check the savings balance for member M001?"
    response_2 = executor.invoke({"input": test_query_2})
    print(f"\nFinal Answer: {response_2['output']}\n")
    
    print("--- Test 3: Combined Tools (Complex Question) ---")
    # This question requires BOTH tools. The agent must check the balance, 
    # then check the policy to see if they qualify for a loan.
    test_query_3 = "I am member M002. Based on my current savings, am I eligible for a 100,000 KES loan?"
    response_3 = executor.invoke({"input": test_query_3})
    print(f"\nFinal Answer: {response_3['output']}\n")