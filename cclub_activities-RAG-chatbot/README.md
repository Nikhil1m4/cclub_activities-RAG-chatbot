#  RAG Backend Service (FastAPI & LangChain)

A role-filtered Retrieval-Augmented Generation (RAG) REST API backend for the Jugaad Robotics Club AI Assistant.

##  Key Responsibilities & Features

- **Vector-Level Role-Based Access Control (RBAC):** Enforces data privacy at the database retrieval tier using ChromaDB metadata filters (`$eq` for public, `$in` for member access).
- **LCEL Pipeline:** Engineered with LangChain Expression Language (`RunnableParallel`) for parallel context retrieval, source document extraction, and LLM inference.
- **Source Citation Mapping:** Staps source document metadata (`Member_Database` / `Public_Database`) onto responses for verifiable claims.
- **Dynamic Follow-Up Questions:** Prompts the model to yield structured contextual follow-up suggestions (`SUGGESTIONS: ...`).

##  Tech Stack

- **Framework:** FastAPI (Python) & Uvicorn
- **Orchestration:** LangChain LCEL
- **LLM Engine:** Groq API (`llama-3.3-70b-versatile` / Llama 3.3 70B)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Local execution)
- **Vector Database:** ChromaDB

##  API Specification

### `POST /chat`
**Request Payload:**
```json
{
  "message": "What is the team budget?",
  "role": "member",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello! How can I help you today?" }
  ]
}
```

**Response Payload:**
```json
{
  "answer": "The annual budget is...",
  "role": "member",
  "sources": ["Member_Database"]
}
```

### `GET /health`
Returns `{"status": "ok"}` for container/service health checks.

##  Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Environment configuration (.env)
echo "GROQ_API_KEY=your_groq_api_key" > .env

# 3. Build knowledge PDFs (optional)
python create_pdfs.py

# 4. Launch FastAPI server
python main.py
```
