# Role-Based RAG Chatbot

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?style=for-the-badge&logo=langchain)
![Llama3](https://img.shields.io/badge/Llama_3.3_70B-0466C8?style=for-the-badge)

A full-stack Retrieval-Augmented Generation (RAG) chatbot built with FastAPI and React, developed for the Jugaad Robotics Club at UIET Chandigarh. The project explores practical RAG patterns — role-based access control, conversational memory, and source citations — in a real club context.

## Key Features

- **Role-Based Access Control (RBAC):** Metadata filtering at the vector-database level (ChromaDB) ensures public visitors cannot query member-only documents, without any LLM-side filtering.
- **Source Citations:** Uses LangChain's `RunnableParallel` to extract the retrieved document chunks alongside the LLM answer, displaying source badges in the UI so responses are traceable.
- **Multi-Turn Memory:** Chat history is passed with each request to the backend, allowing the model to handle contextual follow-ups across a conversation.
- **Follow-Up Suggestions:** The LLM is prompted to append structured follow-up questions, which the frontend parses and renders as clickable buttons.
- **Groq Inference:** Uses the Groq API (`llama-3.3-70b-versatile`) for fast LLM responses without running a local GPU.

## Stack

- **Frontend:** React (Vite) + Vanilla CSS
- **Backend:** Python + FastAPI
- **AI Orchestration:** LangChain Expression Language (LCEL)
- **Vector Database:** ChromaDB
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (runs locally)
- **LLM:** Groq API

## Getting Started

### 1. Backend

```bash
cd cclub_activities-RAG-chatbot
pip install -r requirements.txt
# Copy .env.example to .env and add your GROQ_API_KEY
python main.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` to use the chatbot.

## Design Decisions

1. **Groq over OpenAI:** Groq's LPU inference gives noticeably faster response times, which matters for a chat UI. No cost concerns for a student project either.
2. **Vector-level filtering over LLM-level filtering:** RBAC is enforced via ChromaDB's `$eq`/`$in` metadata filters at query time, not by asking the LLM to self-censor. This is more reliable and guarantees no data leakage regardless of prompt behavior.
3. **LCEL over legacy LangChain chains:** `RunnableParallel` lets the pipeline retrieve context and source documents in a single pass, keeping the chain readable and avoiding a second retrieval call.

---

⭐ If you found this project useful as a reference, consider giving it a star — it helps others find it too.
FUTURE GOALS : make a 3 role (Admin , Member,Public User)  based access so I can make my complete project in a way that same chatbot handles queries from public user,club member and the member and admin can upload data in form of pdf and only admin can insert and manage these uploaded pdfs in rag pipeline.

📄 **License:** This project is built for educational purposes. Feel free to reference or adapt it for your own learning.
