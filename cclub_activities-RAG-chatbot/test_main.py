import os
import sys
from unittest.mock import MagicMock

# Set fallback env var for test execution if no live key is set
if not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "gsk_your_groq_api_key_here":
    os.environ["GROQ_API_KEY"] = "test_key_placeholder"

from langchain_core.messages import AIMessage
from fastapi.testclient import TestClient
import main

def test_rag_service():
    print("--- Starting FastAPI Integration Test ---")
    
    with TestClient(main.app) as client:
        # Override llm AFTER lifespan has completed startup
        if os.environ.get("GROQ_API_KEY") == "test_key_placeholder":
            mock_llm = MagicMock()
            ai_msg = AIMessage(content="Linux Unleashed was a beginner-friendly Linux workshop.")
            mock_llm.invoke.return_value = ai_msg
            mock_llm.return_value = ai_msg
            mock_llm._type = "chat"
            main.llm = mock_llm

        # 1. Health check endpoint
        res = client.get("/health")
        print(f"GET /health -> Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

        # 2. Public role query
        public_req = {"message": "What is the Linux Unleashed workshop about?", "role": "public"}
        res = client.post("/chat", json=public_req)
        print(f"\nPOST /chat (role='public', message='{public_req['message']}'):")
        print(f"Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
        assert res.json()["role"] == "public"

        # 3. Member role query
        member_req = {"message": "What is the internal budget allocation?", "role": "member"}
        res = client.post("/chat", json=member_req)
        print(f"\nPOST /chat (role='member', message='{member_req['message']}'):")
        print(f"Status: {res.status_code}, Response: {res.json()}")
        assert res.status_code == 200
        assert res.json()["role"] == "member"

        print("\n--- All Backend Endpoints & Role Logic Verified! ---")

if __name__ == "__main__":
    test_rag_service()
