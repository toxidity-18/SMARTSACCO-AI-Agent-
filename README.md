
# SmartSACCO AI Agent

## Project Overview

SmartSACCO AI is an enterprise-grade AI assistant designed specifically for Savings and Credit Cooperatives (SACCOs) and financial institutions. It bridges the gap between static, unstructured policy documents and live, structured relational database records, providing users with accurate, context-aware financial guidance.

The system utilizes Retrieval-Augmented Generation (RAG) to query official SACCO policies locally (ensuring strict data privacy and sovereignty) and Tool Calling (Function Calling) to fetch real-time member financial data via a secure REST API. 

## Architecture

The application is built using a modular, microservices-inspired architecture designed for scalability and maintainability:

- **Backend (FastAPI):** Exposes secure, parameterized RESTful endpoints for querying the SQLite relational database containing member financial data.
- **Knowledge Brain (LangChain + ChromaDB):** Processes PDF policy documents into vector embeddings using local, open-source Hugging Face models. This enables semantic search without sending sensitive corporate data to third-party cloud APIs.
- **AI Agent (Google Gemini):** Acts as the central orchestration layer. It dynamically analyzes user intent and decides whether to query the live database or the local vector store, combining the results into a coherent natural language response.
- **Frontend (Streamlit):** Provides a clean, responsive, and interactive chat interface for the end-user, managing session state and chat history.
- **Infrastructure (Docker):** Fully containerized deployment ensuring environment consistency, reproducible builds, and seamless orchestration across development and production environments.

## Technical Stack

- **Language:** Python 3.11
- **Web Framework:** FastAPI, Uvicorn
- **AI Orchestration:** LangChain, LangChain Classic
- **LLM:** Google Gemini (gemini-flash-latest)
- **Embeddings:** Hugging Face `sentence-transformers` (all-MiniLM-L6-v2) - *Deployed locally for data privacy*
- **Database:** SQLite (Relational), ChromaDB (Vector)
- **Frontend:** Streamlit
- **Containerization:** Docker, Docker Compose

## API Documentation

The backend exposes a REST API for integrating with other enterprise systems or external frontends.

### Base URL
`http://localhost:8000`

### Endpoints

#### 1. Health Check
- **URL:** `/`
- **Method:** `GET`
- **Description:** Verifies the API server is running.
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

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.11 or higher
- Docker and Docker Compose (required only for containerized deployment)
- A free Google AI Studio API Key (for the LLM reasoning engine)

## Local Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
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

## Running the Application

### Option 1: Local Execution (Development)

1. Start the FastAPI backend in one terminal:
   ```bash
   uvicorn backend.main:app --reload
   ```
2. Start the Streamlit frontend in a second terminal:
   ```bash
   streamlit run frontend/app.py
   ```
3. Access the interactive AI chat interface in your browser at: `http://localhost:8501`
4. Access the auto-generated API documentation (Swagger UI) at: `http://localhost:8000/docs`

### Option 2: Docker Compose (Recommended for Deployment)

Run the following command in the root directory to build and start both the API and the frontend in isolated, orchestrated containers:

```bash
docker-compose up --build
```

- Access the API documentation at: `http://localhost:8000/docs`
- Access the AI Chat Interface at: `http://localhost:8501`

## Testing the AI Agent

You can test the agent's tool-calling capabilities, reasoning loop, and tool-switching logic directly from the terminal without the frontend:

```bash
python backend/agent.py
```

This script executes predefined test queries that demonstrate the agent's ability to:
1. Query the local RAG pipeline for policy rules.
2. Query the REST API for live member data.
3. Combine both data sources to make complex eligibility decisions.
```

---

