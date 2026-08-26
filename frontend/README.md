#  RAG Chatbot Frontend (React + Vite)

A modern, responsive single-page web interface for interacting with the Role-Based RAG FastAPI backend.

##  Key Features

- **Role Switching UI:** Real-time toggle between ` Public Visitor` and ` Verified Member` roles to demonstrate vector-level security rules.
- **Source Badges:** Renders transparent citation badges (` Source: Member_Database`) returned by backend document retrieval.
- **Proactive Follow-up Suggestions:** Automatically parses hidden backend suggestion markers into interactive, single-click prompt buttons.
- **Conversational Memory:** Preserves multi-turn chat history state and sends history context on each prompt to backend API.
- **Glassmorphism UI:** Custom-built dark mode CSS layout with smooth auto-scrolling and typing indicators.

##  Tech Stack

- **Core Framework:** React 18 + Vite
- **Styling:** Custom Vanilla CSS (Glassmorphism & dark-mode aesthetic)
- **Markdown Processing:** `react-markdown`

##  Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev

# 3. Build production bundle
npm run build
```
