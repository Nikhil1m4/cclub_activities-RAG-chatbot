# Enterprise-Grade RAG Chatbot

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-FFFFFF?style=for-the-badge&logo=langchain)
![Llama3](https://img.shields.io/badge/Llama_3.3_70B-0466C8?style=for-the-badge)

A full-stack, context-aware Retrieval-Augmented Generation (RAG) system built with FastAPI and React. This project was engineered to demonstrate enterprise-level AI patterns, focusing on data security, conversational memory, and source traceability.

##  Key Features

- **Role-Based Access Control (RBAC):** Implements strict metadata filtering at the vector-database level (ChromaDB) so that public visitors can never access or query member-only confidential documents.
- **Source Traceability (Citations):** Utilizes Langchain's advanced `RunnableParallel` to extract raw database chunks alongside the LLM inference, rendering transparent source badges (e.g., `📄 Source: Member_Database`) in the UI to prevent hallucinations.
- **Multi-Turn Conversational Memory:** Maintains chat history state between the React frontend and FastAPI backend, allowing the LLM to understand contextual follow-up questions (e.g., "What is the budget?" -> "Who manages it?").
- **Proactive UX:** The LLM is strictly prompted to dynamically generate context-aware follow-up questions, which are parsed by the frontend into clickable suggestion buttons.
- **High-Performance Inference:** Powered by Meta's Llama 3.3 (70B parameters) running on Groq's LPU inference engine for blazing-fast token streaming.

##  Architecture Stack

- **Frontend:** React (Vite) + Vanilla CSS (Glassmorphism UI)
- **Backend API:** Python + FastAPI 
- **AI Orchestration:** LangChain Expression Language (LCEL)
- **Vector Database:** ChromaDB (Local Dense Vector Search)
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
- **LLM:** Groq API (`llama-3.3-70b-versatile`)

##  Getting Started

### 1. Backend Setup
```bash
cd cclub_activities-RAG-chatbot
pip install -r requirements.txt
# Add your GROQ_API_KEY to a .env file
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to interact with the bot!

##  Technical Trade-offs & Decisions
Here are some specific architectural choices made for this project:
1. **Groq over OpenAI:** Chosen for its industry-leading token generation speed, which is critical for maintaining a snappy user experience in real-time chat applications.
2. **Vector Filtering vs Post-Retrieval Masking:** Security rules (Public vs Member) are enforced directly within the ChromaDB query (`$in` operators) rather than relying on the LLM to censor itself. This guarantees zero data leakage.
3. **LCEL (Langchain Expression Language):** Chose LCEL over legacy Langchain chains because of its modern, declarative syntax and native support for asynchronous parallel execution (`RunnableParallel`).
