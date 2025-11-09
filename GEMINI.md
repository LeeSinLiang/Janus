# Project Janus

This document provides a comprehensive overview of Project Janus, a multi-agent system for automating go-to-market strategies.

## Project Overview

Janus is a web application with a Python backend and a Next.js frontend. The backend is a Django application that uses LangChain and Google Generative AI to create a multi-agent system for marketing automation. The frontend is a Next.js application that provides a user interface for interacting with the backend.

**Backend:**

*   **Framework:** Django
*   **AI/ML:** LangChain, LangGraph, Google Generative AI
*   **Key Libraries:** `django`, `langchain`, `langgraph`, `google-generativeai`, `djangorestframework`
*   **Architecture:** 3-layer supervisor pattern with specialized sub-agents for strategy planning, content creation, platform interaction, and metrics analysis.

**Frontend:**

*   **Framework:** Next.js (React)
*   **Key Libraries:** `next`, `react`, `react-dom`

## Building and Running

### Backend

1.  **Install dependencies:**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    ```bash
    cd backend
    cp .env.example .env
    # Edit .env and add your GOOGLE_API_KEY
    ```

3.  **Run Django migrations:**
    ```bash
    cd backend/src
    python manage.py migrate
    ```

4.  **Run the development server:**
    ```bash
    cd backend/src
    python manage.py runserver
    ```

### Frontend

1.  **Install dependencies:**
    ```bash
    cd frontend/janus
    npm install
    ```

2.  **Run the development server:**
    ```bash
    cd frontend/janus
    npm run dev
    ```

## Development Conventions

*   The backend follows a modular design, with agents and their tools separated into different files.
*   The backend uses a 3-layer supervisor pattern for agent orchestration.
*   The frontend is a standard Next.js application.
*   The project uses placeholder data for testing, which can be found in `backend/src/agents/data/placeholder_metrics.json`.

## Testing

### Backend

*   **Test individual agents:**
    ```bash
    cd backend/src
    python -m agents.content_creator
    python -m agents.strategy_planner
    python -m agents.supervisor
    ```
*   **Run Django tests:**
    ```bash
    cd backend/src
    python manage.py test agents
    ```
