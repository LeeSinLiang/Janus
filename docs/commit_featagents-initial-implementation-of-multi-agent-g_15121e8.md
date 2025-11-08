# Documentation for Commit 15121e8

**Commit Hash:** 15121e8bd85289d856f71fa50948466f07b91488
**Commit Message:** feat(agents): initial implementation of multi-agent GTM OS with LangChain and Gemini
**Generated:** Fri Nov  7 21:47:54 EST 2025
**Repository:** aiatl

---

# Git Diff Analysis: Janus Backend - Multi-Agent System Introduction

## 1. Summary

This extensive diff introduces the foundational backend for "Janus," an AI-powered Go-To-Market (GTM) Operating System. The core change is the implementation of a multi-agent system using **LangChain and Google Generative AI (Gemini)**, following a 3-layer supervisor pattern. This update establishes a robust framework for automating marketing strategies, content creation, X (Twitter) platform interaction, and metrics analysis.

## 2. Changes

### 2.1. New Multi-Agent System Architecture
A 3-layer supervisor pattern is implemented, comprising:
*   **Layer 3: Orchestrator (`supervisor.py`)**: Coordinates sub-agents, routes requests, and synthesizes workflows.
*   **Layer 2: Specialized Sub-Agents**:
    *   `StrategyPlannerAgent`: Creates marketing strategies and Mermaid diagrams.
    *   `ContentCreatorAgent`: Generates A/B content variants.
    *   `XPlatformAgent`: Handles X (Twitter) posting and scheduling.
    *   `MetricsAnalyzerAgent`: Analyzes performance and provides insights.
*   **Layer 1: Low-Level Tools (`tools.py`)**: Provides basic functionalities like posting tweets, fetching metrics, and validating content.

### 2.2. LangChain and Google Gemini Integration
The system leverages `langchain-google-genai` for all LLM interactions, primarily using the `"gemini-2.5-flash"` model. Agents are initialized using `ChatGoogleGenerativeAI` and either `create_agent()` for tool-using agents or direct `prompt | model | parser` chains for content generation.

### 2.3. Environment Configuration
New `.env` and `.env.example` files are introduced for managing API keys (`GOOGLE_API_KEY`, `LANGSMITH_API_KEY`) and other settings.

### 2.4. In-Memory State Management
A new `state.py` module provides in-memory data structures (`Campaign`, `Post`, `ContentVariant`, `AgentMemory`) for managing campaign context and agent history.

### 2.5. Placeholder Data for Testing
`src/agents/data/placeholder_metrics.json` is added, containing mock X (Twitter) metrics, enabling full system testing without live API integrations.

### 2.6. Comprehensive Documentation & Demo
*   `README.md`: Project overview, detailed architecture, installation, and usage.
*   `QUICKSTART.md`: Concise setup and quick examples.
*   `IMPLEMENTATION_NOTES.md`: Deep dive into LangChain/Gemini patterns and best practices.
*   `demo.py`: A runnable script showcasing the entire multi-agent workflow.

### 2.7. Django Integration
*   `src/janus/settings.py` is updated to include `rest_framework`, `core`, and `agents` apps.
*   Centralized `AGENT_SETTINGS` are added for model and temperature configurations.

## 3. Impact

*   **Enhanced Capabilities**: The system can now autonomously plan, create, execute, and analyze marketing campaigns.
*   **Structured AI Workflows**: Complex GTM tasks are broken down into manageable, specialized agent interactions.
*   **Improved Developer Experience**: Comprehensive documentation (`README`, `QUICKSTART`, `IMPLEMENTATION_NOTES`) and a runnable `demo.py` significantly ease onboarding and understanding.
*   **Testability**: Placeholder data allows for local development and testing of agent logic without external API dependencies.
*   **Scalability**: The modular agent design facilitates future expansion with new agents, tools, and platforms.

## 4. Usage

### 4.1. Installation & Setup
1.  **Install dependencies**: `pip install -r requirements.txt`
2.  **Configure environment**:
    ```bash
    cp .env.example .env
    # Edit .env and add your GOOGLE_API_KEY
    ```
3.  **Run Django migrations**:
    ```bash
    cd src
    python manage.py migrate
    ```

### 4.2. Running the Demo
Execute `python demo.py` from the `backend/` directory to see the multi-agent system in action.

### 4.3. Agent Interaction (Python Examples)
```python
from agents import create_orchestrator, create_content_creator

# Orchestrator
orchestrator = create_orchestrator()
result = orchestrator.execute("Create a marketing strategy for my SaaS product")
print(result['output'])

# Content Creator
content_agent = create_content_creator()
content = content_agent.create_content("Create a tweet about our AI tool")
print(content['variants'][0]['content'])
```

## 5. Breaking Changes

None. This is a new system introduction.

## 6. Migration Notes

For existing Django projects, ensure `INSTALLED_APPS` in `src/janus/settings.py` includes `rest_framework`, `core`, and `agents`. Also, add the `REST_FRAMEWORK` and `AGENT_SETTINGS` dictionaries to your `settings.py`. New projects can simply use the provided `settings.py`.