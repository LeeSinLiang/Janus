# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Janus is an AI-powered GTM (Go-To-Market) OS for technical founders, built as a multi-agent system using LangChain and Google Gemini. It automates marketing strategy planning, content creation with A/B testing, and metrics-driven optimization across social platforms (primarily X/Twitter).

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (requires Google API key from https://ai.google.dev/gemini-api/docs/api-key)
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Run Django migrations
cd src && python manage.py migrate
```

### Testing
```bash
# Test complete 3-scenario workflow (from backend directory)
python demo.py
# Scenario 1: Strategy Planning → Mermaid Diagram → Save to DB
# Scenario 2: Generate A/B Content for all nodes
# Scenario 3: Metrics Analysis → Improved Content

# Test individual agents (from src directory)
cd src
python -m agents.supervisor        # Orchestrator
python -m agents.content_creator   # Content generation
python -m agents.strategy_planner  # Strategy planning
python -m agents.x_platform        # X/Twitter operations
python -m agents.metrics_analyzer  # Metrics analysis
```

### Django Development
```bash
cd src
python manage.py runserver         # Start dev server
python manage.py test agents       # Run Django tests
python manage.py makemigrations    # Create migrations
```

## Architecture: 3-Layer Supervisor Pattern

Janus implements LangChain's supervisor pattern with three distinct layers:

### Layer 3: Orchestrator (supervisor.py)
- **Pattern**: `create_agent()` with sub-agents wrapped as `@tool` decorators
- **Role**: Routes user requests to specialized agents, synthesizes multi-agent workflows
- **Invocation**: `agent.invoke({"messages": [{"role": "user", "content": text}]})`
- **Key Point**: Sub-agents are exposed as tools that the supervisor can call

### Layer 2: Specialized Sub-Agents
Two distinct implementation patterns:

**Agent Pattern** (supervisor.py, x_platform.py, metrics_analyzer.py):
- Uses `create_agent()` with tool collections
- Orchestrates tool calls based on natural language requests
- Returns: `{"output": str, "raw_result": dict}` after extracting from messages

**Structured Output Pattern** (content_creator.py, strategy_planner.py):
- Uses `create_agent()` with `response_format=PydanticModel`
- LangChain automatically selects strategy (ProviderStrategy for native support, ToolStrategy otherwise)
- Direct structured output generation via Pydantic models
- Returns: Pydantic object (e.g., `ContentOutput`, `StrategyOutput`)
- **Note**: Temperature set to 0 for consistent structured output

### Layer 1: Low-Level Tools (tools.py)
- Decorated with `@tool` from `langchain_core.tools`
- Individual operations: `post_tweet`, `get_metrics`, `validate_tweet_format`, etc.
- Currently use placeholder data from `src/agents/data/placeholder_metrics.json`

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

### State Management Pattern

**Database-backed persistent storage** using Django ORM in `state.py` (migrated from in-memory):

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

**Django Models** (in `models.py`):
- `Campaign`: Campaigns with phase, strategy (Mermaid), insights[], metadata{}
- `Post`: Posts linked to campaigns with status, phase, metrics{}
- `ContentVariant`: A/B variants linked to posts with content, platform, metadata{}
- `AgentMemory`: Agent context{} and history[] stored as JSON
- `ConversationMessage`: Conversation history with optional campaign link

All data persists to SQLite database with indexed fields for performance.

## Agent-Specific Patterns

### Supervisor Agent (supervisor.py)
Wraps sub-agents as tools for the orchestrator:
```python
@tool
def create_marketing_strategy(request: str) -> str:
    """Tool docstring becomes function description for LLM."""
    result = self.strategy_planner.execute(...)
    return json.dumps(result.model_dump())  # Convert Pydantic to JSON
```

### Content Creator + Strategy Planner
- Use `create_agent()` with `response_format=PydanticModel`
- Pydantic schemas define expected output (e.g., `ContentOutput`, `StrategyOutput`)
- Agent invocation: `agent.invoke({"messages": [{"role": "user", "content": text}]})`
- Returns: Pydantic object with validated fields
- Public API: `execute()` method extracts and returns Pydantic object directly

**Example**:
```python
# Content Creator
output = content_agent.execute(title, description, product_info)
print(output.A)  # Access variant A
print(output.B)  # Access variant B

# Strategy Planner
output = strategy_agent.execute(product_description, gtm_goals)
print(output.diagram)  # Access Mermaid diagram
```

### X Platform + Metrics Analyzer
- Use `create_agent()` with tool arrays
- Tools are domain-specific operations (post, validate, analyze)
- Extract output via `_extract_output()` helper method
- Return format: `{"output": str, "raw_result": dict}`

## Key Files Structure

```
src/agents/
├── __init__.py           # Agent exports, factory functions
├── supervisor.py         # Layer 3: Orchestrator
├── strategy_planner.py   # Layer 2: Strategy + Mermaid generation (structured output)
├── content_creator.py    # Layer 2: A/B content generation (structured output)
├── x_platform.py         # Layer 2: X/Twitter operations (agent with tools)
├── metrics_analyzer.py   # Layer 2: Metrics analysis (agent with tools)
├── tools.py              # Layer 1: Low-level @tool functions
├── state.py              # Database-backed state management (Django ORM)
├── models.py             # Django models: Campaign, Post, ContentVariant, etc.
├── mermaid_parser.py     # Parse Mermaid diagrams into nodes/connections
├── admin.py              # Django admin for managing campaigns and data
└── data/
    └── placeholder_metrics.json  # Mock X API data for testing

Root directory:
├── demo.py               # 3-scenario demo workflow (strategy → content → metrics)

src/janus/
└── settings.py           # Django config, AGENT_SETTINGS for temperatures
```

## Common Pitfalls

1. **Import Errors**: Do NOT use `init_chat_model()` or `AgentExecutor` - these are old patterns
2. **Model Names**: Use `"gemini-2.5-flash"` NOT `"google_genai:gemini-2.5-flash"`
3. **Agent Invocation**: Use `agent.invoke({"messages": [...]})` NOT `executor.invoke({"input": ...})`
4. **Type Handling**: When extracting `response.content`, cast to `str()` to avoid list type issues
5. **Structured Output**: Use `response_format=PydanticModel` in `create_agent()`, NOT `JsonOutputParser` chain pattern
6. **Temperature for Structured Output**: Always use temperature=0 for agents returning structured data (content_creator, strategy_planner)

## Django Integration

- Apps: `core` (empty), `agents` (multi-agent system with database models)
- Settings: `AGENT_SETTINGS` dict configures model temperatures per agent
- Database: SQLite with Django ORM for persistent storage
- Models: Campaign, Post, ContentVariant, AgentMemory, ConversationMessage
- Admin: Full Django admin interface registered for all models
- REST Framework configured but not yet used (future: API endpoints for React frontend)
- Environment: Load `.env` with `python-dotenv` for `GOOGLE_API_KEY`

**Database Schema:**
- Campaigns track phases, store Mermaid diagrams, and link to posts
- Posts have A/B variants (ContentVariant) and metrics stored as JSON
- Posts support many-to-many relationships (next_posts) for campaign flow
- Agent memories persist context and history between sessions
- Conversation messages optionally link to campaigns for context

**Mermaid Diagram Workflow:**
1. Strategy Planner generates Mermaid diagram with custom node format:
   - Nodes: `NODEX[<title>Title</title><description>Description</description>]`
   - Exactly 3 subgraphs: "Phase 1", "Phase 2", "Phase 3"
   - Connections: `NODE1 --> NODE2`
2. Mermaid parser extracts nodes and connections from diagram string
3. Create Campaign with strategy field containing Mermaid diagram
4. Create Post objects for each node, link via next_posts M2M relationship
5. Frontend renders Mermaid diagram for visual campaign planning

## Future Extensions (Post-Hackathon)

From notes/janus.md:
- Real X/Twitter API integration (currently placeholder)
- ProductHunt API integration
- Trigger detection engine (e.g., "if ER < 1.5% after 2h → swap variant B")
- Vector DB integration for semantic campaign search (current: SQLite)
- Upgrade to PostgreSQL for production deployment
- Django REST API for React frontend
- ReactFlow canvas for visual campaign editing

**Completed:**
- ✅ Persistent database storage with Django ORM (migrated from in-memory)
- ✅ Django admin interface for data management
- ✅ Mermaid diagram storage in Campaign model
