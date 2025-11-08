# Janus - AI-Powered GTM OS Backend

Multi-agent system for automating go-to-market strategies for technical founders.

## Architecture

Janus implements a **3-layer supervisor pattern** using LangChain:

### Layer 1: Low-Level Tools
- X (Twitter) API tools
- Metrics fetching and analysis tools
- Content generation utilities

### Layer 2: Specialized Sub-Agents
- **Strategy Planner Agent**: Creates marketing strategies and generates Mermaid diagrams
- **Content Creator Agent**: Generates A/B content variants optimized for engagement
- **X Platform Agent**: Handles posting, scheduling, and X-specific operations
- **Metrics Analyzer Agent**: Analyzes metrics and provides actionable insights

### Layer 3: Orchestrator (Supervisor)
- Coordinates all sub-agents
- Routes user requests to appropriate agents
- Synthesizes multi-agent workflows

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Run Django migrations:**
```bash
cd src
python manage.py migrate
```

## Quick Start

### Using the Orchestrator (Recommended)

```python
from agents import create_orchestrator

# Initialize the orchestrator
orchestrator = create_orchestrator()

# Example 1: Create a campaign strategy
result = orchestrator.execute(
    "Create a marketing strategy for Janus, an AI GTM OS for technical founders. "
    "Goal: Launch and get first 100 users in 4 weeks."
)
print(result['output'])

# Example 2: Generate content with A/B variants
result = orchestrator.execute(
    "Generate tweet content announcing our product launch with A/B variants"
)
print(result['output'])

# Example 3: Analyze metrics
result = orchestrator.execute(
    "Analyze platform insights and recommend optimal posting times"
)
print(result['output'])
```

### Using Individual Agents

#### Strategy Planner Agent
```python
from agents import create_strategy_planner

agent = create_strategy_planner()

strategy = agent.create_strategy(
    product_info="AI-powered marketing automation for developers",
    campaign_goal="Launch on ProductHunt and X",
    context={"timeline": "2 weeks", "channels": ["X", "ProductHunt"]}
)

print(f"Campaign: {strategy['campaign_name']}")
print(f"Mermaid Diagram:\n{strategy['mermaid_diagram']}")
```

#### Content Creator Agent
```python
from agents import create_content_creator

agent = create_content_creator()

content = agent.create_content(
    request="Create a tweet about our AI marketing tool",
    context={"brand_voice": "technical, friendly", "target_audience": "developers"}
)

# Get A/B variants
print(f"Variant A: {content['variants'][0]['content']}")
print(f"Variant B: {content['variants'][1]['content']}")
```

#### X Platform Agent
```python
from agents import create_x_platform_agent

agent = create_x_platform_agent()

# Post a tweet
result = agent.post(
    content="Excited to launch our AI GTM OS! 🚀",
    validate_first=True
)

# Schedule a tweet
result = agent.schedule(
    content="Check out our new features!",
    optimize_time=True  # Finds optimal posting time
)
```

#### Metrics Analyzer Agent
```python
from agents import create_metrics_analyzer

agent = create_metrics_analyzer()

# Analyze a specific tweet
analysis = agent.analyze_tweet("tweet_001")

# Compare A/B variants
comparison = agent.compare_ab_variants("tweet_001", "tweet_002")

# Get platform insights
insights = agent.get_platform_insights()
```

## Complete Workflow Example

```python
from agents import create_orchestrator

orchestrator = create_orchestrator()

# Run a complete campaign workflow
results = orchestrator.run_campaign_workflow(
    product_info="Janus - AI GTM OS for technical founders",
    campaign_goal="Launch and acquire first 100 users",
    execute_immediately=False  # Set to True to post content
)

print("Strategy:", results['strategy'])
print("Content:", results['content'])
print("Analysis:", results['analysis'])
```

## State Management

Janus uses in-memory state management for the hackathon:

```python
from agents import state

# Create a campaign
campaign = state.create_campaign(
    campaign_id="campaign_001",
    name="Product Launch",
    description="Launch Janus to tech founders"
)

# Get campaign
campaign = state.get_campaign("campaign_001")

# Update campaign strategy
state.update_campaign_strategy(
    "campaign_001",
    "graph TD\n    A[Start] --> B[Phase 1]"
)

# Add insights
state.add_campaign_insight("campaign_001", "Engagement up 45%")
```

## Testing with Placeholder Data

The system includes realistic placeholder X (Twitter) metrics in `src/agents/data/placeholder_metrics.json`:

- Tweet metrics (views, likes, retweets, engagement rates)
- Platform insights (best posting times, trending topics)
- Content performance data
- A/B test results

This allows you to test the full agent workflow without real API access.

## Project Structure

```
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py          # Agent exports
│   │   ├── supervisor.py        # Orchestrator Agent
│   │   ├── strategy_planner.py  # Strategy Planner Agent
│   │   ├── content_creator.py   # Content Creator Agent
│   │   ├── x_platform.py        # X Platform Agent
│   │   ├── metrics_analyzer.py  # Metrics Analyzer Agent
│   │   ├── tools.py             # Low-level tools
│   │   ├── state.py             # State management
│   │   └── data/
│   │       └── placeholder_metrics.json
│   ├── janus/                   # Django project
│   │   └── settings.py
│   └── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Key Features

✅ **Multi-Agent Architecture**: Following LangChain supervisor pattern
✅ **A/B Testing**: Automatic generation of 2 variants for every content
✅ **Mermaid Diagrams**: Visual campaign strategies for React integration
✅ **In-Memory State**: Fast local state management
✅ **Placeholder Metrics**: Test without real API access
✅ **Modular Design**: Easy to swap components and add features

## Next Steps (Post-Hackathon)

- [ ] Integrate real X (Twitter) API
- [ ] Add ProductHunt API integration
- [ ] Implement long-term memory with PostgreSQL/Vector DB
- [ ] Add trigger detection engine (if ER < 1.5% → swap variant)
- [ ] Create Django REST API endpoints
- [ ] Add webhook support for real-time metrics
- [ ] Implement campaign scheduling and automation

## Configuration

Agent settings can be configured in `src/janus/settings.py`:

```python
AGENT_SETTINGS = {
    "DEFAULT_MODEL": "gemini-2.0-flash-exp",
    "CONTENT_CREATOR_TEMPERATURE": 0.7,
    "X_PLATFORM_TEMPERATURE": 0.3,
    "METRICS_ANALYZER_TEMPERATURE": 0.4,
    "STRATEGY_PLANNER_TEMPERATURE": 0.6,
    "ORCHESTRATOR_TEMPERATURE": 0.5,
}
```

## Running Tests

```bash
# Test individual agents
cd src
python -m agents.content_creator
python -m agents.strategy_planner
python -m agents.supervisor

# Run Django tests
python manage.py test agents
```

## License

MIT License - Built for the AI Atlanta Hackathon

## Contributing

This is a hackathon project with plans to open-source. Contributions welcome after the event!
