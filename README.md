
# SmartSACCO AI Agent

## Executive Summary

SmartSACCO AI is an enterprise-grade, conversational AI assistant designed specifically for Savings and Credit Cooperatives (SACCOs) and financial institutions. It bridges the critical gap between static, unstructured corporate policy documents and live, structured relational database records. 

By leveraging Retrieval-Augmented Generation (RAG) and advanced Tool Calling (Function Calling), the system provides users with highly accurate, context-aware financial guidance. Crucially, the RAG pipeline utilizes local, open-source embedding models to ensure that sensitive corporate policy documents never leave the internal network, addressing strict enterprise data privacy and sovereignty requirements.

## Architecture and Design Philosophy

The application is built using a decoupled, microservices-inspired architecture. Rather than relying on a monolithic structure, the system separates the data processing layer, the AI orchestration layer, and the user interface layer.

1. **The AI Agent (The Orchestrator):** The core of the application is a LangChain Agent powered by Google Gemini. It acts as a reasoning engine. Instead of hallucinating answers, it analyzes user intent and dynamically routes the query to the appropriate "tool."
2. **The Knowledge Brain (RAG Pipeline):** For queries regarding corporate rules, interest rates, or eligibility criteria, the agent queries a local ChromaDB vector store. We intentionally use the Hugging Face `all-MiniLM-L6-v2` model for text embeddings. This runs entirely on-premise, ensuring that sensitive SACCO policy documents are not sent to third-party cloud APIs for vectorization.
3. **The Data Ledger (REST API):** For queries regarding specific member accounts, balances, or loan statuses, the agent executes an HTTP GET request to a custom FastAPI backend, which queries a relational SQLite database.
4. **Decoupled Deployment:** The compute-heavy backend is hosted on Render, while the user-facing frontend is hosted on Streamlit Community Cloud. This ensures a zero-latency user experience while keeping the backend scalable and secure.

## Technical Stack

- **Language:** Python 3.11
- **Web Framework (Backend):** FastAPI, Uvicorn
- **AI Orchestration:** LangChain, LangChain Classic
- **Large Language Model (LLM):** Google Gemini (`gemini-flash-latest`)
- **Vector Database:** ChromaDB
- **Embeddings:** Hugging Face `sentence-transformers` (`all-MiniLM-L6-v2`) - *Deployed locally for data privacy*
- **Relational Database:** SQLite
- **Frontend Framework:** Streamlit
- **Cloud Infrastructure:** Render (Backend API), Streamlit Community Cloud (Frontend UI)

## Interactive Testing Guide

To fully demonstrate the capabilities of the SmartSACCO AI Agent, users should test the system using the following specific prompts. These prompts are designed to trigger the different tools available to the AI.

### Test 1: Policy and Rule Retrieval (RAG Tool)
**Prompt:** 
> "What is the interest rate for development loans, and what is the maximum loan amount a member can get?"

**Expected Behavior:** 
The AI will recognize this as a general policy question. It will invoke the local RAG tool, search the vectorized PDF documents, and return the exact interest rates (e.g., 1% per month on a reducing balance) and the loan multiplier rules (e.g., 4 times the member's deposits) directly from the official SACCO Credit Policy document.

### Test 2: Live Account Data Retrieval (REST API Tool)
**Prompt:** 
> "What is the current savings balance and account status for member M001?"

**Expected Behavior:** 
The AI will recognize this as a specific account query. It will invoke the REST API tool, make an HTTP request to the FastAPI backend, retrieve the live JSON data for member "M001" (John Kamau), and format the response into natural language (e.g., "Member M001, John Kamau, has an active account with a savings balance of 150,000 KES").

### Test 3: Complex Multi-Step Reasoning (Combined Tools)
**Prompt:** 
> "I am member M002. Based on my current savings, am I eligible for a 100,000 KES development loan?"

**Expected Behavior:** 
This is the ultimate test of the AI's reasoning capabilities. The agent will:
1. First, invoke the REST API tool to fetch the current savings balance for member "M002" (Mary Wanjiku).
2. Second, invoke the RAG tool to fetch the official loan eligibility rules from the policy documents.
3. Finally, it will combine both pieces of information, apply the logic (e.g., checking if the balance multiplied by 4 is greater than 100,000), and provide a definitive, logically sound "Yes" or "No" answer with an explanation.

## API Documentation

The backend exposes a secure REST API that can be integrated with other enterprise systems or external frontends.

### Base URL
`https://smartsacco-backend.onrender.com` (Production) or `http://localhost:8000` (Local)

### Endpoints

#### 1. Health Check
- **URL:** `/`
- **Method:** `GET`
- **Description:** Verifies the API server is running and healthy.
- **Response:** 
  ```json
  {
    "status": "SmartSACCO API is running",
    "version": "1.0.0"
  }
  ```

#### 2. Get Member Financial Summary
- **URL:** `/api/members/{member_id}/financial-summary`
- **Method:** `GET`
- **Description:** Retrieves the complete financial profile for a specific member.
- **Path Parameter:** `member_id` (string, e.g., "M001")
- **Success Response (200 OK):**
  ```json
  {
    "member_id": "M001",
    "full_name": "John Kamau",
    "account_status": "Active",
    "savings_balance": 150000.0,
    "outstanding_loan_balance": 30000.0
  }
  ```
- **Error Response (404 Not Found):** 
  ```json
  {
    "detail": "Member not found"
  }
  ```

## Deployment Architecture

The application is deployed using a decoupled, best-of-breed cloud strategy to ensure optimal performance and cost-efficiency.

- **Backend API (Render):** The FastAPI server, SQLite database, and ChromaDB vector store are hosted on Render. This environment handles the heavy computational lifting, including AI reasoning and database queries. It is configured using environment variables to securely manage API keys.
- **Frontend UI (Streamlit Community Cloud):** The Streamlit interface is hosted on Streamlit's native cloud platform. This ensures the user interface loads instantly with zero "cold start" latency, providing a seamless experience for the end-user. The frontend communicates securely with the Render backend via REST over the public internet.

## Local Setup and Installation

For developers who wish to run or contribute to the project locally, follow these steps.

### Prerequisites
- Python 3.11 or higher
- Git
- A free Google AI Studio API Key

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/toxidity-18/SMARTSACCO-AI-Agent-.git
   cd SMARTSACCO-AI-Agent-
   ```

2. **Set up the virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your Google API key:
   ```text
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

5. **Initialize the Database and Vector Store:**
   ```bash
   python backend/database.py
   python backend/rag.py
   ```

6. **Run the Application Locally:**
   Open two separate terminal windows.
   
   *Terminal 1 (Backend):*
   ```bash
   uvicorn backend.main:app --reload
   ```
   
   *Terminal 2 (Frontend):*
   ```bash
   streamlit run frontend/app.py
   ```
   Access the local interface at `http://localhost:8501`.

## Project Structure

```text
SMARTSACCO-AI-Agent-/
├── backend/
│   ├── main.py              # FastAPI REST API endpoints
│   ├── database.py          # SQLite database initialization and mock data
│   ├── rag.py               # RAG pipeline (PDF loading, chunking, vectorization)
│   ├── agent.py             # LangChain AI Agent and Tool definitions
│   └── chroma_db/           # Local persisted vector database (gitignored)
├── frontend/
│   └── app.py               # Streamlit user interface
├── data/
│   └── policies/            # Raw SACCO policy PDF documents
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Security and Data Privacy

This project was designed with enterprise security in mind. 
- **Local Embeddings:** By using `all-MiniLM-L6-v2` for the RAG pipeline, sensitive SACCO policy documents are vectorized locally. They are never transmitted to external embedding APIs (like OpenAI), mitigating data leakage risks.
- **Environment Variables:** All sensitive credentials, including the Google API Key and backend URLs, are strictly managed via environment variables and are never hardcoded into the source code.
- **Decoupled Communication:** The frontend and backend communicate over HTTPS using standard REST protocols, ensuring secure data transit.
