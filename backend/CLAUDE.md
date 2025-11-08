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
# Test complete system (from backend directory)
python demo.py

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

**Chain Pattern** (content_creator.py, strategy_planner.py):
- Uses LCEL: `prompt | model | JsonOutputParser`
- Direct structured output generation
- Returns: Dictionary matching Pydantic schema
- **Critical**: JSON examples in prompts MUST escape braces with `{{` and `}}`

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

### Structured Output with JsonOutputParser

For chain-based agents (content_creator, strategy_planner):

```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
    field: str = Field(description="...")

parser = JsonOutputParser(pydantic_object=OutputSchema)
chain = prompt | model | parser
result = chain.invoke({"request": user_input})  # Returns dict
```

**CRITICAL**: When including JSON examples in ChatPromptTemplate prompts, escape all braces:
```python
# WRONG - will cause "missing variables" error
"""Return JSON: {"field": "value"}"""

# CORRECT
"""Return JSON: {{"field": "value"}}"""
```

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
    result = self.strategy_planner.create_strategy(...)
    return json.dumps(result)  # Return JSON string from tool
```

### Content Creator + Strategy Planner
- Use `JsonOutputParser(pydantic_object=Schema)` for structured output
- Pydantic schemas define expected output format with Field descriptions
- Chain invocation: `chain.invoke({"request": text})`
- Parser automatically validates and returns typed dict

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
├── strategy_planner.py   # Layer 2: Strategy + Mermaid generation (chain)
├── content_creator.py    # Layer 2: A/B content generation (chain)
├── x_platform.py         # Layer 2: X/Twitter operations (agent)
├── metrics_analyzer.py   # Layer 2: Metrics analysis (agent)
├── tools.py              # Layer 1: Low-level @tool functions
├── state.py              # Database-backed state management (Django ORM)
├── models.py             # Django models: Campaign, Post, ContentVariant, etc.
├── admin.py              # Django admin for managing campaigns and data
└── data/
    └── placeholder_metrics.json  # Mock X API data for testing

src/janus/
└── settings.py           # Django config, AGENT_SETTINGS for temperatures
```

## Common Pitfalls

1. **Import Errors**: Do NOT use `init_chat_model()` or `AgentExecutor` - these are old patterns
2. **Model Names**: Use `"gemini-2.5-flash"` NOT `"google_genai:gemini-2.5-flash"`
3. **Prompt Templates**: Always escape JSON braces as `{{` and `}}` in system prompts
4. **Agent Invocation**: Use `agent.invoke({"messages": [...]})` NOT `executor.invoke({"input": ...})`
5. **Type Handling**: When extracting `response.content`, cast to `str()` to avoid list type issues

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
- Agent memories persist context and history between sessions
- Conversation messages optionally link to campaigns for context

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
