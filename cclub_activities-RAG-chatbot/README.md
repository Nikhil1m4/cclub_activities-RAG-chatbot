# 🤖 Jugaad Club AI Assistant

A fast, interactive Retrieval-Augmented Generation (RAG) chatbot designed to answer queries about the Jugaad Robotics Club's activities, achievements, and events. 

This project uses a custom knowledge base (PDF document) to provide context-aware, accurate answers without hallucinations, leveraging local embeddings and lightning-fast LLM inference.

## 🚀 Features
*   **Document Q&A:** Answers questions based entirely on the provided `club_activities.pdf` knowledge base.
*   **Lightning-Fast Inference:** Powered by Groq's Llama 4 Scout (17B) model for near-instantaneous text generation.
*   **Free Local Embeddings:** Utilizes Hugging Face's `all-MiniLM-L6-v2` model to generate embeddings locally, avoiding API costs for vectorization.
*   **Interactive UI:** A clean, soft-themed chat interface built with Gradio for seamless user interaction.

## 🛠️ Tech Stack
*   **Language:** Python
*   **Framework:** [LangChain](https://www.langchain.com/)
*   **LLM:** Meta Llama 4 Scout (via [Groq API](https://groq.com/))
*   **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
*   **Vector Database:** ChromaDB
*   **Frontend:** Gradio

## 📋 Prerequisites
Before running this project, ensure you have the following installed:
*   Python 3.8 or higher
*   A valid [Groq API Key](https://console.groq.com/keys)

## ⚙️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/your-username/jugaad-club-ai-assistant.git](https://github.com/your-username/jugaad-club-ai-assistant.git)
cd jugaad-club-ai-assistant
