"""
Jugaad Robotics Club — Role-Based RAG Chatbot (FastAPI Backend)
================================================================
Architecture: Single FastAPI service that trusts the "role" field
forwarded by the upstream Node.js authentication layer. This service
is ONLY responsible for retrieval-augmented generation (RAG) and
role-based knowledge filtering. Authentication is NOT handled here.
"""

import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from operator import itemgetter
from pydantic import BaseModel, field_validator

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ---------------------------------------------------------------------------
# Load environment variables from .env file (if it exists).
# load_dotenv() is a no-op when .env is absent, so this is safe in production
# where secrets come from the OS environment directly (e.g., Docker/k8s).
# ---------------------------------------------------------------------------
load_dotenv()

# Global state — populated once at startup, shared across all requests.
vector_db: Chroma | None = None
llm: ChatGroq | None = None


# Pydantic models

class ChatRequest(BaseModel):
    message: str
    role: str = "public"
    history: list[dict] = []

    # Validate role values so bad requests fail fast with a clear 422 response.
    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in ("public", "member"):
            raise ValueError('role must be "public" or "member"')
        return v

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    answer: str
    role: str
    sources: list[str] = []


class HealthResponse(BaseModel):
    status: str


# Document ingestion helpers

def ingest_pdf(path: str, access_level: str) -> list:
    """
    Load a PDF, split it into chunks, and stamp each chunk's metadata with
    its access level.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required PDF not found: '{path}'")

    loader = PyPDFLoader(path)
    documents = loader.load()

    # chunk_size=1000 keeps context windows manageable.
    # chunk_overlap=100 ensures sentences split across chunk boundaries are
    # still represented in at least one chunk — prevents lost context.
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # Stamp access level onto every chunk's metadata.
    # ChromaDB stores this alongside the vector and uses it for $eq/$in filters.
    for chunk in chunks:
        chunk.metadata["access"] = access_level

    return chunks


# Application lifespan (startup / shutdown)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Everything before `yield` runs at startup; after `yield` runs at shutdown.
    """
    global vector_db, llm

    # 1. Validate GROQ_API_KEY
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(
            "\n[FATAL] GROQ_API_KEY environment variable is not set.\n"
            "  → For local dev: add GROQ_API_KEY=gsk_... to a .env file.\n"
            "  → For production: set it as an OS/container environment variable.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Ingest both PDFs
    print("[Startup] Loading and ingesting PDF documents...")
    try:
        public_chunks = ingest_pdf("public.pdf", access_level="public")
        member_chunks = ingest_pdf("member.pdf", access_level="member")
        all_chunks = public_chunks + member_chunks
        print(
            f"[Startup] Ingested {len(public_chunks)} public chunks "
            f"and {len(member_chunks)} member chunks "
            f"({len(all_chunks)} total)."
        )
    except FileNotFoundError as e:
        print(f"\n[FATAL] {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Build embeddings + ChromaDB
    print("[Startup] Building embeddings and ChromaDB index (this may take a moment)...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        persist_dir = "./chroma_db"
        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            print(f"[Startup] Loading existing ChromaDB index from '{persist_dir}'...")
            vector_db = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings,
            )
        else:
            print(f"[Startup] Building new ChromaDB index and persisting to '{persist_dir}'...")
            vector_db = Chroma.from_documents(
                documents=all_chunks,
                embedding=embeddings,
                persist_directory=persist_dir,
            )
        print("[Startup] ChromaDB index initialized successfully.")
    except Exception as e:
        print(f"\n[FATAL] ChromaDB initialization failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Initialize the LLM
    llm = ChatGroq(
        model_name="openai/gpt-oss-20b",
        temperature=0,       # temperature=0 → deterministic, factual answers.
        groq_api_key=api_key,
    )
    print("[Startup] LLM (ChatGroq / Llama 3.3 70b) initialized.")
    print("[Startup] Service is ready. [OK]\n")

    yield  # ← server is live and handling requests between here and shutdown

    # Shutdown logic (if needed) goes here.
    print("[Shutdown] Cleaning up resources.")


# FastAPI app

app = FastAPI(
    title="Jugaad Club RAG API",
    description="Role-based retrieval-augmented generation backend for the Jugaad Robotics Club chatbot.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG prompt template
RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are the AI assistant for the Jugaad Robotics Club. Answer questions using ONLY the information provided in the context below.

Guidelines:
- Exception: If the user is just greeting you (e.g., "hello", "hi"), greet them back professionally and ask how you can help them today. Do NOT mention the context.
- Keep answers brief and high-level — 2 to 4 sentences maximum.
- If the question is technical (e.g., asking about an algorithm, codebase, or process), describe WHAT it is and its general purpose. Do NOT explain step-by-step implementation details, even if the context includes them.
- Use a neutral, professional, direct tone. No emojis, no puns, no dramatic language.
- If the context does not contain enough information, say so plainly and directly — do not apologize dramatically.

At the very end of your response, on a new line, provide exactly 3 short follow-up questions the user can ask based on the context. Format them EXACTLY like this:
SUGGESTIONS: <Related Question 1> || <Related Question 2> || <Related Question 3>

Conversation History:
{chat_history}

Context:
{context}
Question: {question}
Answer:"""
)


def format_docs(docs) -> str:
    """Concatenate retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(role: str):
    """
    Build a role-filtered LCEL RAG chain on the fly for each request.
    """
    if role == "public":
        # Public users may only see chunks explicitly tagged as public.
        chroma_filter = {"access": {"$eq": "public"}}
    else:
        # Members see everything: public info AND internal member-only content.
        chroma_filter = {"access": {"$in": ["public", "member"]}}

    retriever = vector_db.as_retriever(
        search_kwargs={"k": 3, "filter": chroma_filter}
    )

    from langchain_core.runnables import RunnableParallel
    
    # LCEL chain: retriever → format → prompt → LLM → parse string output
    setup_and_retrieval = RunnableParallel(
        context=itemgetter("question") | retriever | format_docs,
        docs=itemgetter("question") | retriever,
        question=itemgetter("question"),
        chat_history=itemgetter("chat_history")
    )
    
    chain = setup_and_retrieval.assign(
        answer=RAG_PROMPT | llm | StrOutputParser()
    )
    return chain


# Endpoints

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Simple liveness probe. Returns 200 {"status": "ok"} when the service is
    running. Check this endpoint before connecting any frontend or load balancer.
    """
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Accepts a user message and role, runs the LCEL RAG chain, and returns the AI's answer.
    """
    if vector_db is None or llm is None:
        # Should not happen if startup succeeded, but guard defensively.
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Vector database or LLM failed to initialize.",
        )

    try:
        # Build chain on the fly with the requested role
        rag_chain = build_rag_chain(role=request.role)
        
        # Format the chat history for the prompt (keeping only the last 4 messages for token efficiency)
        chat_history = ""
        if request.history:
            chat_history = "\n".join([f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in request.history[-4:]])

        # Invoke LCEL pipeline
        # Notice how cleanly we pass the input dict to the chain.
        result = rag_chain.invoke({
            "question": request.message,
            "chat_history": chat_history
        })
        
        # Extract and map custom source names
        raw_sources = set()
        for doc in result.get("docs", []):
            src = doc.metadata.get("source", "")
            if src:
                filename = os.path.basename(src).lower()
                if "member" in filename:
                    raw_sources.add("Member_Database")
                elif "public" in filename:
                    raw_sources.add("Public_Database")
                else:
                    raw_sources.add(filename)

        return ChatResponse(
            answer=result["answer"], 
            role=request.role, 
            sources=list(raw_sources)
        )

    except Exception as e:
        # Catch-all for unexpected LLM/retriever errors. Log the full error
        # server-side but return a clean message to the client.
        print(f"[ERROR] /chat failed for role='{request.role}': {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the response: {str(e)}",
        )


# Entry point

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" makes the service reachable from other machines (e.g., the
    # Node.js auth layer). Use "127.0.0.1" if you want localhost-only access.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
