# SmartSACCO AI Agent

> A conversational AI prototype for SACCOs and financial institutions that combines **LLMs, Retrieval-Augmented Generation (RAG), tool calling, REST APIs, and structured financial data**.

## Overview

SmartSACCO AI is a conversational AI assistant designed to demonstrate how an LLM-powered application can work with both **unstructured knowledge** and **structured financial data**.

Instead of relying entirely on the language model to generate answers, the system gives the AI agent access to specialized tools:

- A **RAG tool** for retrieving information from SACCO policy documents.
- A **REST API tool** for retrieving member financial information from a relational database.

This allows the assistant to answer simple policy questions, retrieve live member information, and combine information from multiple sources when handling more complex questions.

The project also explores a privacy-conscious approach to document retrieval by generating embeddings locally using the Hugging Face `all-MiniLM-L6-v2` model rather than sending policy documents to an external embedding API.

> **Project status:** Learning and demonstration prototype. It is not intended for production financial use.

---

## Why I Built This

I built SmartSACCO AI to explore how LLM applications can interact with real software systems instead of only generating text.

I wanted to understand how an AI assistant could:

1. Understand a user's question.
2. Determine what information is required.
3. Retrieve information from a knowledge base when necessary.
4. Retrieve structured data through an API when necessary.
5. Use information from multiple sources to produce a contextual response.

The project gave me practical experience working with:

- LLM applications
- AI agents
- Retrieval-Augmented Generation
- Tool/function calling
- REST APIs
- FastAPI
- Vector databases
- Relational databases
- Cloud deployment
- Environment-based configuration

---

# Key Features

### AI Agent

A LangChain-based agent powered by Google Gemini interprets user questions and determines which available tool should be used.

### Retrieval-Augmented Generation

SACCO policy documents are processed and stored in a ChromaDB vector store.

The system retrieves relevant sections of the policy documents when the user asks questions about rules, interest rates, loan eligibility, or other policy-related information.

### 🔧 Tool Calling

The AI agent can call different tools depending on the user's request.

Currently available tools include:

- Policy/RAG retrieval
- Member financial information API

### 🏦 Member Financial Data

A FastAPI backend provides access to demonstration member financial data stored in SQLite.

The API can return information such as:

- Member name
- Account status
- Savings balance
- Outstanding loan balance

### 🔐 Local Embeddings

The `all-MiniLM-L6-v2` embedding model runs locally during the RAG process.

This means the policy documents do not need to be sent to an external embedding provider for vectorization.

### ☁️ Cloud Deployment

The project uses a decoupled deployment approach:

- **Backend:** Render
- **Frontend:** Streamlit Community Cloud

The frontend communicates with the backend through REST APIs.

---

# System Architecture

SmartSACCO AI uses a decoupled architecture with separate components for the user interface, AI orchestration, knowledge retrieval, and structured data access.

```text
                         ┌───────────────────┐
                         │       User        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Streamlit UI    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   LangChain AI    │
                         │      Agent        │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │     RAG Tool     │          │     API Tool     │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │     ChromaDB     │          │     FastAPI      │
          │   Vector Store   │          │      Backend     │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ SACCO Policy     │          │     SQLite       │
          │    Documents     │          │     Database     │
          └──────────────────┘          └──────────────────┘
```

---

# How the AI Agent Works

The AI agent acts as the orchestration layer between the user and the available data sources.

When a user submits a question, the agent analyzes the request and determines whether it requires:

- Information from SACCO policy documents
- Information from member records
- Information from both sources

For example:

```text
User Question
      │
      ▼
AI Agent
      │
      ├── Policy question ──────► RAG Tool
      │                              │
      │                              ▼
      │                         ChromaDB
      │
      ├── Member question ──────► REST API Tool
      │                              │
      │                              ▼
      │                           FastAPI
      │                              │
      │                              ▼
      │                           SQLite
      │
      └── Complex question ─────► Multiple tools
```

The retrieved information is then provided to the LLM so that it can formulate a contextual response.

---

# RAG Pipeline

The Retrieval-Augmented Generation pipeline is responsible for answering questions based on SACCO policy documents.

## Process

```text
Policy Documents
       │
       ▼
Document Loading
       │
       ▼
Text Chunking
       │
       ▼
Local Embeddings
(all-MiniLM-L6-v2)
       │
       ▼
ChromaDB Vector Store
       │
       ▼
User Question
       │
       ▼
Similarity Search
       │
       ▼
Relevant Document Chunks
       │
       ▼
LLM Context
       │
       ▼
Generated Response
```

## Embedding Model

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embedding model runs locally.

This approach was selected to demonstrate how sensitive policy documents can be processed without requiring the documents to be sent to an external embedding API.

---

# Tool Calling

The AI agent has access to multiple tools.

## 1. RAG Tool

The RAG tool is intended for questions involving information contained in SACCO policy documents.

Examples include:

- Loan interest rates
- Loan eligibility requirements
- Loan limits
- SACCO rules
- Policy requirements

Example:

```text
"What is the interest rate for development loans?"
```

The agent can use the RAG tool to retrieve the relevant policy information.

---

## 2. Member Financial API Tool

The API tool is intended for questions involving specific member information.

Examples include:

- Savings balance
- Account status
- Outstanding loan balance
- Member financial information

Example:

```text
"What is the current savings balance for member M001?"
```

The agent can call the REST API and retrieve the relevant member data.

---

## 3. Multi-Tool Reasoning

The system can also demonstrate a more complex workflow where multiple sources are required.

Example:

```text
"I am member M002. Based on my current savings,
am I eligible for a 100,000 KES development loan?"
```

A possible workflow is:

```text
User Question
      │
      ▼
AI Agent
      │
      ├──────────────► Member API
      │                    │
      │                    ▼
      │             Savings Balance
      │
      └──────────────► RAG Tool
                           │
                           ▼
                    Loan Policy Rules
                           │
                           ▼
                    Agent combines
                    retrieved context
                           │
                           ▼
                    Eligibility Assessment
```

The assessment is based on the retrieved policy information and member data.

---

# Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| AI Orchestration | LangChain |
| LLM | Google Gemini |
| RAG | LangChain + ChromaDB |
| Vector Database | ChromaDB |
| Embeddings | Hugging Face / Sentence Transformers |
| Embedding Model | `all-MiniLM-L6-v2` |
| Relational Database | SQLite |
| Frontend | Streamlit |
| Backend Deployment | Render |
| Frontend Deployment | Streamlit Community Cloud |
| Version Control | Git / GitHub |

---

# API Documentation

The backend exposes a REST API that can be used by the frontend and AI agent.

## Base URL

Production:

```text
https://smartsacco-backend.onrender.com
```

Local:

```text
http://localhost:8000
```

---

## Health Check

### Endpoint

```http
GET /
```

### Description

Checks whether the API server is running.

### Example Response

```json
{
  "status": "SmartSACCO API is running",
  "version": "1.0.0"
}
```

---

# Get Member Financial Summary

### Endpoint

```http
GET /api/members/{member_id}/financial-summary
```

### Description

Retrieves the financial summary for a specific demonstration member.

### Example

```http
GET /api/members/M001/financial-summary
```

### Example Response

```json
{
  "member_id": "M001",
  "full_name": "John Kamau",
  "account_status": "Active",
  "savings_balance": 150000.0,
  "outstanding_loan_balance": 30000.0
}
```

### Member Not Found

```json
{
  "detail": "Member not found"
}
```

---

# Example Queries

The following examples can be used to test the system.

## Test 1 — Policy Retrieval

```text
What is the interest rate for development loans,
and what is the maximum loan amount a member can get?
```

### Expected Workflow

The agent identifies this as a policy-related question and uses the RAG tool to retrieve the relevant information from the SACCO policy documents.

---

## Test 2 — Member Data Retrieval

```text
What is the current savings balance and account status
for member M001?
```

### Expected Workflow

The agent identifies this as a member-specific question and calls the FastAPI financial-summary endpoint.

---

## Test 3 — Multi-Tool Query

```text
I am member M002. Based on my current savings,
am I eligible for a 100,000 KES development loan?
```

### Expected Workflow

The agent can:

1. Retrieve the member's financial information using the API tool.
2. Retrieve the relevant loan eligibility rules using the RAG tool.
3. Combine the retrieved information.
4. Provide an eligibility assessment based on the available information.

---

# Deployment Architecture

The project separates the frontend and backend services.

```text
                   Internet
                      │
                      ▼
          ┌──────────────────────┐
          │ Streamlit Community  │
          │       Cloud          │
          │                      │
          │    Frontend UI       │
          └──────────┬───────────┘
                     │
                     │ HTTPS / REST
                     ▼
          ┌──────────────────────┐
          │       Render         │
          │                      │
          │     FastAPI API      │
          │          │           │
          │     ┌────┴────┐      │
          │     ▼         ▼      │
          │  SQLite    ChromaDB  │
          └──────────────────────┘
```

## Backend

The FastAPI backend is deployed on Render.

It handles:

- API requests
- Database access
- RAG retrieval
- AI agent operations

## Frontend

The Streamlit frontend is deployed using Streamlit Community Cloud.

It provides the conversational interface through which users interact with the AI assistant.

---

# Security and Data Privacy Considerations

The project was designed with several privacy and security considerations in mind.

## Local Embeddings

The RAG pipeline uses the local:

```text
all-MiniLM-L6-v2
```

embedding model.

Policy documents therefore do not need to be transmitted to an external embedding provider during vectorization.

## Environment Variables

Sensitive configuration such as API keys is managed using environment variables.

Example:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

API keys should not be committed to source control.

## HTTPS Communication

The deployed frontend communicates with the production backend through HTTPS.

---

# Important Prototype Limitations

SmartSACCO AI is a learning and demonstration project and should not be treated as a production financial system.

Current limitations include:

- The member database contains demonstration/mock data.
- SQLite is used instead of a production database system.
- Production-grade authentication and authorization have not been implemented.
- The system does not connect to a real SACCO core banking system.
- Production-grade audit logging has not been implemented.
- Comprehensive monitoring and observability are not yet implemented.
- AI-generated responses require validation before being used in real financial decision-making.
- The current eligibility workflow demonstrates the technical concept rather than replacing formal SACCO lending processes.
- The system has not undergone the security, compliance, and reliability testing required for production financial software.

These limitations provide areas for future development.

---

# Future Improvements

Potential improvements include:

- Add user authentication and role-based authorization.
- Replace SQLite with PostgreSQL or another production database.
- Add comprehensive API validation and error handling.
- Add automated unit and integration tests.
- Introduce structured logging and monitoring.
- Add audit trails for AI tool calls and financial-data access.
- Improve RAG evaluation and retrieval accuracy.
- Add document versioning.
- Add citation/source references to RAG responses.
- Introduce deterministic business rules for financial eligibility calculations.
- Add human approval workflows for sensitive financial decisions.
- Containerize the application using Docker.
- Explore MCP for standardized AI-to-tool communication.
- Evaluate LangGraph or other orchestration approaches for more complex workflows.
- Add stronger authentication between frontend and backend services.

---

# Project Structure

```text
SMARTSACCO-AI-Agent-/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── rag.py
│   ├── agent.py
│   └── chroma_db/
│
├── frontend/
│   └── app.py
│
├── data/
│   └── policies/
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Backend Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI application and REST endpoints |
| `database.py` | SQLite database initialization and demonstration data |
| `rag.py` | Document processing, embeddings, and ChromaDB retrieval |
| `agent.py` | LangChain agent and tool definitions |
| `chroma_db/` | Persisted local vector store |

### Frontend

| File | Purpose |
|---|---|
| `app.py` | Streamlit user interface |

---

# Local Setup

## Prerequisites

Install the following:

- Python 3.11+
- Git
- Google AI Studio API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/toxidity-18/SMARTSACCO-AI-Agent-.git
cd SMARTSACCO-AI-Agent-
```

---

## 2. Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

Do not commit the `.env` file to Git.

---

## 5. Initialize the Database

```bash
python backend/database.py
```

---

## 6. Initialize the RAG Vector Store

```bash
python backend/rag.py
```

This processes the available policy documents and creates the local ChromaDB vector store.

---

## 7. Start the Backend

Open a terminal and run:

```bash
uvicorn backend.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

---

## 8. Start the Frontend

Open another terminal:

```bash
streamlit run frontend/app.py
```

The Streamlit application will normally be available at:

```text
http://localhost:8501
```

---

# Environment Variables

The following environment variables are required:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Gemini API key |

Additional environment variables may be required depending on the deployment configuration.

---

# What I Learned

This project helped me gain practical experience with the architecture and development of LLM-powered applications.

Key areas I explored include:

- Python backend development
- FastAPI REST APIs
- LangChain agents
- LLM integration
- Retrieval-Augmented Generation
- Vector databases
- Local embedding models
- Tool/function calling
- Connecting AI agents to REST APIs
- Relational databases
- Frontend/backend separation
- Cloud deployment
- Environment-variable management
- Data privacy considerations for AI applications

One of the main lessons from the project was that useful AI applications require more than an LLM. The surrounding architecture — including data retrieval, APIs, tools, validation, security, and application logic — plays an important role in making an AI system useful.

---

# Project Status

**Status:** Active learning / portfolio project

The project is functional as a demonstration of an AI agent interacting with both unstructured policy information and structured member data.

Further development is planned around security, testing, production database infrastructure, observability, deterministic business logic, and more advanced AI-to-tool communication.

