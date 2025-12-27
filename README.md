# News Agent (Cognitive Architecture)

> **For LLMs**: This repository contains a ReAct-based agentic pipeline built with LangGraph, Gemini 1.5 Pro, and Mailjet. It uses dynamic web search (DuckDuckGo) to research topics defined in `src/topics.yaml`.

## 🧠 System Architecture (Context for AI)
 If you are an AI assistant reading this, here is the system's mental model:
*   **Core Logic**: `src/main.py` initializes a `StateGraph` from `src/agent/graph.py`.
*   **Cognitive Loop**: `Planner` -> `Researcher` (DuckDuckGo) -> `Writer` (Gemini).
*   **State Management**: `src/agent/state.py` defines `AgentState` (`topic`, `messages`, `research_results`, `summary`).
*   **Delivery**: `src/mailer.py` uses Mailjet API to send HTML digests.
*   **Configuration**: All secrets live in `.env` (Google API Key, Mailjet Keys).

## 🚀 Human Quick Start

### Prerequisites
*   Docker installed.
*   API Keys: Google AI Studio (Gemini), Mailjet.

### Setup
1.  **Clone & Config**:
    ```bash
    cp .env.example .env
    # Edit .env with your keys:
    # GOOGLE_API_KEY=...
    # MAILJET_API_KEY=...
    # MAILJET_SECRET_KEY=...
    ```

2.  **Run with Docker** (Recommended):
    ```bash
    docker build -t news-agent .
    docker run --env-file .env news-agent
    ```

3.  **Customize Topics**:
    Edit `src/topics.yaml`:
    ```yaml
    topics:
      - "Generative AI Infrastructure"
      - "SpaceX Starship Updates"
    ```

## 📂 Project Structure
*   `src/agent/`: Contains the "Brain" (Graph, Tools, State).
*   `src/main.py`: Entry point. Orchestrates the agent -> database -> mailer pipeline.
*   `data/`: Persistent storage (SQLite).

---
*Created by [Your Name/Bot]*
