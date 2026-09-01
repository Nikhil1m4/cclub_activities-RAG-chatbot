import os
import sys
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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

load_dotenv()

vector_db: Chroma | None = None
llm: ChatGroq | None = None


class ChatRequest(BaseModel):
    message: str
    role: str = "public"
    history: list[dict] = []

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


def ingest_pdf(path: str, access_level: str) -> list:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required PDF not found: '{path}'")

    loader = PyPDFLoader(path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["access"] = access_level

    return chunks


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_db, llm

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(
            "\n[FATAL] GROQ_API_KEY environment variable is not set.\n"
            "  For local dev: add GROQ_API_KEY=gsk_... to a .env file.\n"
            "  For production: set it as an OS/container environment variable.\n",
            file=sys.stderr,
        )
        sys.exit(1)

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

    llm = ChatGroq(
        model_name="openai/gpt-oss-20b",
        temperature=0,
        groq_api_key=api_key,
    )
    print("[Startup] LLM initialized.")
    print("[Startup] Service is ready. [OK]\n")

    yield

    print("[Shutdown] Cleaning up resources.")


app = FastAPI(
    title="Jugaad Club RAG API",
    description="Role-based retrieval-augmented generation backend for the Jugaad Robotics Club chatbot.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(role: str):
    if role == "public":
        chroma_filter = {"access": {"$eq": "public"}}
    else:
        chroma_filter = {"access": {"$in": ["public", "member"]}}

    retriever = vector_db.as_retriever(
        search_kwargs={"k": 3, "filter": chroma_filter}
    )

    from langchain_core.runnables import RunnableParallel

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


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.post("/upload", tags=["Upload"])
async def upload_pdf(
    file: UploadFile = File(...),
    role: str = Form(...),
):
    if role not in ("public", "member"):
        raise HTTPException(
            status_code=400,
            detail='role must be "public" or "member".',
        )

    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    if vector_db is None:
        raise HTTPException(status_code=503, detail="Vector database not ready.")

    existing = vector_db.get(
        where={"source": {"$contains": file.filename}}
    )
    if existing and existing.get("ids"):
        raise HTTPException(
            status_code=409,
            detail=f"A file named '{file.filename}' has already been ingested. Delete it from the database before re-uploading.",
        )

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(temp_dir, unique_name)

    file_bytes = await file.read()
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    chunks = []
    try:
        chunks = ingest_pdf(temp_path, access_level=role)
        vector_db.add_documents(chunks)
        print(f"[Upload] Ingested '{file.filename}' as role='{role}' ({len(chunks)} chunks added).")
    except Exception as e:
        print(f"[ERROR] /upload failed for '{file.filename}': {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process the uploaded file: {str(e)}",
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_added": len(chunks),
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    if vector_db is None or llm is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Vector database or LLM failed to initialize.",
        )

    try:
        rag_chain = build_rag_chain(role=request.role)

        chat_history = ""
        if request.history:
            chat_history = "\n".join([f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in request.history[-4:]])

        result = rag_chain.invoke({
            "question": request.message,
            "chat_history": chat_history
        })

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
        print(f"[ERROR] /chat failed for role='{request.role}': {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the response: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
