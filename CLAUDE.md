# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Janus is an AI-powered GTM (Go-To-Market) OS for technical founders. It automates marketing strategy planning, content creation with A/B testing, and metrics-driven optimization using a multi-agent system built with LangChain and Google Gemini.

**Tech Stack:**
- **Backend**: Django 5.2.8 + LangChain + Google Gemini (gemini-2.5-flash)
- **Frontend**: Next.js 16 (React 19) + TypeScript + Tailwind CSS + ReactFlow
- **Database**: SQLite (Django ORM)
- **API**: Django REST Framework with CORS

## Development Commands

### Backend Setup & Development

```bash
# Setup (from backend directory)
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY from https://ai.google.dev/gemini-api/docs/api-key

# Run migrations
cd src && python manage.py migrate

# Start Django server
python manage.py runserver  # http://localhost:8000

# Create new migrations
python manage.py makemigrations

# Django admin
python manage.py createsuperuser
```

### Frontend Setup & Development

```bash
# Setup (from frontend/janus directory)
cd frontend/janus
npm install

# Development
npm run dev     # http://localhost:3000
npm run build
npm start
npm run lint
```

### Testing

```bash
# Backend - Run complete 3-scenario demo (from backend directory)
python demo.py
# Scenario 1: Strategy Planning → Mermaid Diagram → Save to DB
# Scenario 2: Generate A/B Content for all nodes
# Scenario 3: Metrics Analysis → Improved Content

# Backend - Test individual agents (from backend/src directory)
cd src
python -m agents.supervisor
python -m agents.content_creator
python -m agents.strategy_planner
python -m agents.x_platform
python -m agents.metrics_analyzer

# Backend - Django tests
python manage.py test agents
```

## Architecture Overview

### Three-Tier System Architecture

```
Frontend (Next.js)
      ↕ REST API
Backend (Django)
      ↕
Multi-Agent System (LangChain)
```

### Frontend Architecture (Next.js + ReactFlow)

**Key Components:**
- `Canvas.tsx` / `CanvasWithPolling.tsx`: Main ReactFlow canvas with node visualization
- `ChatBox.tsx`: Chat interface for strategy generation
- `TaskCardNode.tsx`: Custom ReactFlow node component with metrics display
- `NodeVariantModal.tsx`: Modal for viewing/selecting A/B content variants
- `ViewToggle.tsx`, `PhaseBar.tsx`, `WelcomeBar.tsx`: UI controls

**Data Flow:**
- `services/api.ts`: API client functions for backend communication
- `utils/graphParser.ts`: Converts backend data to ReactFlow nodes/edges
- `utils/dagreLayout.ts`: Hierarchical auto-layout using dagre algorithm
- `utils/graphDiff.ts`: Detects changes between graph states for polling updates

**Backend Integration:**
- Polls `/nodesJson/` endpoint for graph updates
- Calls `/api/agents/strategy/` to generate marketing strategies
- Fetches content variants via `/getVariants/?pk=<pk>`
- Approves/posts content via `/api/approve` and `/createXPost/`

### Backend Architecture: 3-Layer Supervisor Pattern

Janus implements LangChain's supervisor pattern with three distinct layers:

#### Layer 3: Orchestrator (`supervisor.py`)
- **Pattern**: `create_agent()` with sub-agents wrapped as `@tool` decorators
- **Role**: Routes user requests to specialized agents, synthesizes multi-agent workflows
- **Invocation**: `agent.invoke({"messages": [{"role": "user", "content": text}]})`
- Sub-agents are exposed as tools that the orchestrator can call

#### Layer 2: Specialized Sub-Agents

**Agent Pattern** (`supervisor.py`, `x_platform.py`, `metrics_analyzer.py`):
- Uses `create_agent()` with tool collections
- Orchestrates tool calls based on natural language requests
- Returns: `{"output": str, "raw_result": dict}` after extracting from messages

**Structured Output Pattern** (`content_creator.py`, `strategy_planner.py`):
- Uses `create_agent()` with `response_format=PydanticModel`
- Direct structured output generation via Pydantic models
- Returns: Pydantic object (e.g., `ContentOutput`, `StrategyOutput`)
- Temperature set to 0 for consistent structured output

#### Layer 1: Low-Level Tools (`tools.py`)
- Decorated with `@tool` from `langchain_core.tools`
- Individual operations: `post_tweet`, `get_metrics`, `validate_tweet_format`, etc.
- Currently use placeholder data from `src/agents/data/placeholder_metrics.json`

### Database Schema (Django ORM)

**Models** (in `backend/src/agents/models.py`):
- **Campaign**: Campaigns with phase, strategy (Mermaid diagram), insights[], metadata{}
- **Post**: Posts linked to campaigns with status, phase, metrics{}
- **ContentVariant**: A/B variants linked to posts with content, platform, metadata{}
- **AgentMemory**: Agent context{} and history[] stored as JSON
- **ConversationMessage**: Conversation history with optional campaign link

Posts have many-to-many relationships (`next_posts`) for campaign flow.

### API Endpoints

**Django URLs** (`backend/src/janus/urls.py`):
- `/admin/` - Django admin interface
- `/api/agents/` - Agent API endpoints (strategy, campaigns)
- `/clone/` - Twitter clone functionality
- `/` (root) - Metrics endpoints

**Agent API** (`backend/src/agents/urls.py`):
- `POST /api/agents/strategy/` - Generate marketing strategy with Mermaid diagram
- `GET /api/agents/campaigns/` - List all campaigns
- `GET /api/agents/campaigns/<campaign_id>/` - Get campaign details with posts

## Critical Implementation Details

### LangChain + Google Gemini Integration

**Correct Model Initialization:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # NOT "google_genai:gemini-2.5-flash"
    temperature=0.7
)
```

**Agent Creation:**
```python
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools=[tool1, tool2],
    system_prompt="Your system prompt here"
)
```

**Agent Invocation (NOT executor.invoke):**
```python
result = agent.invoke({
    "messages": [{"role": "user", "content": user_input}]
})

# Extract output
last_message = result["messages"][-1]
output = last_message.content if hasattr(last_message, 'content') else str(last_message)
```

### Structured Output with response_format

For agents returning structured data (content_creator, strategy_planner):

```python
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
    field: str = Field(description="...")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

agent = create_agent(
    model,
    tools=[],
    system_prompt="Your prompt here",
    response_format=OutputSchema  # Pass Pydantic model directly
)

# Invoke agent
result = agent.invoke({"messages": [{"role": "user", "content": input_text}]})

# Extract structured output from last message
last_message = result["messages"][-1]
output = last_message  # Returns Pydantic object directly
```

**Note**: Use temperature=0 for consistent structured output generation.

### Mermaid Diagram Workflow

1. Strategy Planner generates Mermaid diagram with custom node format:
   - Nodes: `NODEX[<title>Title</title><description>Description</description>]`
   - Exactly 3 subgraphs: "Phase 1", "Phase 2", "Phase 3"
   - Connections: `NODE1 --> NODE2`
2. Mermaid parser (`mermaid_parser.py`) extracts nodes and connections
3. Create Campaign with strategy field containing Mermaid diagram
4. Create Post objects for each node, link via `next_posts` M2M relationship
5. Frontend renders graph using ReactFlow with dagre auto-layout

### State Management Pattern

**Database-backed persistent storage** using Django ORM in `state.py`:

```python
from agents import state

# Create campaign (saved to database)
campaign = state.create_campaign(
    campaign_id="campaign_001",
    name="Product Launch",
    description="Launch campaign"
)

# Update strategy (stores Mermaid diagram in database)
state.update_campaign_strategy(campaign_id, mermaid_diagram)

# Add insights (persisted to Campaign.insights JSON field)
state.add_campaign_insight(campaign_id, "Engagement up 45%")

# Agent memory (stored in AgentMemory model)
state.update_agent_memory("agent_name", {"key": "value"})
state.add_to_agent_history("agent_name", {"action": "...", "timestamp": "..."})

# Add post with variants (creates Post and ContentVariant records)
state.add_post_to_campaign(campaign_id, {
    "post_id": "post_001",
    "phase": "launch",
    "status": "published",
    "variants": [
        {"variant_id": "A", "content": "Tweet A", "platform": "x"},
        {"variant_id": "B", "content": "Tweet B", "platform": "x"}
    ]
})

# Conversation history (saved to ConversationMessage model)
state.add_to_conversation("user", "Create a campaign", campaign_id=campaign_id)
```

## Key Files Reference

### Backend Structure
```
backend/
├── demo.py                   # 3-scenario demo workflow
├── src/
│   ├── manage.py
│   ├── janus/
│   │   ├── settings.py      # Django config, AGENT_SETTINGS
│   │   └── urls.py          # Root URL routing
│   └── agents/
│       ├── supervisor.py     # Layer 3: Orchestrator
│       ├── strategy_planner.py  # Strategy + Mermaid generation
│       ├── content_creator.py   # A/B content generation
│       ├── x_platform.py     # X/Twitter operations
│       ├── metrics_analyzer.py  # Metrics analysis
│       ├── media_creator.py  # Image/video generation
│       ├── tools.py          # Layer 1: Low-level tools
│       ├── state.py          # Database-backed state management
│       ├── models.py         # Django models
│       ├── views.py          # REST API views
│       ├── urls.py           # Agent API routing
│       ├── serializers.py    # DRF serializers
│       ├── mermaid_parser.py # Parse Mermaid diagrams
│       ├── admin.py          # Django admin
│       └── data/
│           └── placeholder_metrics.json  # Mock X API data
```

### Frontend Structure
```
frontend/janus/src/
├── app/
│   ├── page.tsx              # Home page (WelcomePage)
│   ├── layout.tsx            # Root layout
│   └── canvas/
│       └── page.tsx          # Canvas page
├── components/
│   ├── Canvas.tsx            # ReactFlow canvas
│   ├── CanvasWithPolling.tsx # Canvas with polling
│   ├── ChatBox.tsx           # Chat interface
│   ├── TaskCardNode.tsx      # Custom node component
│   ├── NodeVariantModal.tsx  # A/B variant modal
│   ├── ViewToggle.tsx        # View controls
│   ├── PhaseBar.tsx          # Phase indicator
│   ├── WelcomeBar.tsx        # Welcome UI
│   └── ...
├── services/
│   └── api.ts                # API client functions
├── utils/
│   ├── graphParser.ts        # Backend data → ReactFlow
│   ├── dagreLayout.ts        # Auto-layout algorithm
│   └── graphDiff.ts          # Change detection
├── types/
│   └── api.ts                # TypeScript API types
└── styles/
    └── theme.ts              # Theme configuration
```

## Common Pitfalls

1. **Import Errors**: Do NOT use `init_chat_model()` or `AgentExecutor` - these are old patterns
2. **Model Names**: Use `"gemini-2.5-flash"` NOT `"google_genai:gemini-2.5-flash"`
3. **Agent Invocation**: Use `agent.invoke({"messages": [...]})` NOT `executor.invoke({"input": ...})`
4. **Type Handling**: When extracting `response.content`, cast to `str()` to avoid list type issues
5. **Structured Output**: Use `response_format=PydanticModel` in `create_agent()`, NOT `JsonOutputParser` chain pattern
6. **Temperature for Structured Output**: Always use temperature=0 for agents returning structured data
7. **Frontend API**: Backend data uses `next_posts` (plural) and `pk` fields, not singular forms
8. **CORS**: Backend configured for `localhost:3000` - update `settings.py` CORS config if frontend port changes

## Configuration

### Backend Environment Variables (`.env`)
```
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL_CODE=gemini-2.5-flash
X_ACCESS_TOKEN=<optional>
X_ACCESS_TOKEN_SECRET=<optional>
X_BEARER_TOKEN=<optional>
X_API_KEY=<optional>
X_API_SECRET=<optional>
```

### Agent Settings (`backend/src/janus/settings.py`)
```python
AGENT_SETTINGS = {
    "DEFAULT_MODEL": os.getenv("GEMINI_MODEL_CODE"),
    "CONTENT_CREATOR_TEMPERATURE": 0.7,
    "X_PLATFORM_TEMPERATURE": 0.3,
    "METRICS_ANALYZER_TEMPERATURE": 0.4,
    "STRATEGY_PLANNER_TEMPERATURE": 0.6,
    "ORCHESTRATOR_TEMPERATURE": 0.5,
}
```

### Frontend Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Frontend-Backend Integration Points

1. **Strategy Generation**: Frontend ChatBox → `POST /api/agents/strategy/` → Backend creates Campaign + Posts → Frontend polls `/nodesJson/`
2. **Graph Visualization**: Frontend fetches data via `fetchGraphDataV1()` or `fetchGraphDataV2()` → ReactFlow renders with dagre layout
3. **Content Variants**: Frontend opens modal → `GET /getVariants/?pk=<pk>` → Display A/B variants
4. **Node Actions**: Approve (`POST /api/approve`), Post to X (`POST /createXPost/`), Get Metrics (`POST /getXPostMetrics/`)
5. **Polling**: Frontend polls `/nodesJson/` every 5s to detect backend changes (metrics updates, new nodes)

## Django Apps Structure

- **core**: Empty placeholder app
- **agents**: Multi-agent system with all models, views, and agent implementations
- **metrics**: Metrics tracking and API endpoints (root URL)
- **twitter_clone**: Twitter/X clone functionality (`/clone/` URLs)

Django admin is fully configured for Campaign, Post, ContentVariant, AgentMemory, and ConversationMessage models at `/admin/`.
