# Janus Backend - Quick Start Guide

Get up and running with the Janus multi-agent system in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Google API Key (for Gemini)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
nano .env
```

Your `.env` should look like:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Run Django Migrations

```bash
cd src
python manage.py migrate
```

### 4. Test the System

Run the demo script to verify everything works:

```bash
# From the backend directory
python demo.py
```

You should see output demonstrating:
- ✅ Orchestrator coordinating agents
- ✅ Individual agents working
- ✅ State management system

## Usage Examples

### Quick Example - Orchestrator

```python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "janus.settings")
import django
django.setup()

from agents import create_orchestrator

orchestrator = create_orchestrator()
result = orchestrator.execute(
    "Create a marketing strategy for my SaaS product"
)
print(result['output'])
```

### Quick Example - Content Creator

```python
from agents import create_content_creator

agent = create_content_creator()
content = agent.create_content(
    "Create a tweet about our AI marketing automation tool"
)

print("Variant A:", content['variants'][0]['content'])
print("Variant B:", content['variants'][1]['content'])
```

### Quick Example - Strategy Planner

```python
from agents import create_strategy_planner

agent = create_strategy_planner()
strategy = agent.create_strategy(
    product_info="AI GTM OS for developers",
    campaign_goal="Launch and get 100 users"
)

print("Mermaid Diagram:")
print(strategy['mermaid_diagram'])
```

## File Structure

```
backend/
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── supervisor.py    # Main orchestrator
│   │   ├── strategy_planner.py
│   │   ├── content_creator.py
│   │   ├── x_platform.py
│   │   ├── metrics_analyzer.py
│   │   ├── tools.py
│   │   ├── state.py
│   │   └── data/
│   │       └── placeholder_metrics.json
│   └── janus/              # Django project
├── demo.py                 # Demo script
├── requirements.txt
└── README.md              # Full documentation
```

## Troubleshooting

### Error: "GOOGLE_API_KEY not found"
- Make sure you created the `.env` file
- Verify the API key is correct
- Check that python-dotenv is installed

### Error: "No module named 'agents'"
- Make sure you're running from the correct directory
- Django settings must be configured before importing agents

### Error: "ImportError: cannot import name..."
- Run `pip install -r requirements.txt` again
- Check Python version (needs 3.10+)

## Next Steps

1. ✅ **Verify setup** - Run `python demo.py`
2. 📖 **Read full docs** - Check `README.md` for detailed usage
3. 🧪 **Experiment** - Try the examples in the README
4. 🔌 **Integrate** - Connect to your React frontend
5. 🚀 **Deploy** - Add real X API credentials for production

## Agent Capabilities

### Orchestrator Agent
- Coordinates all sub-agents
- Routes complex requests
- Synthesizes multi-agent workflows

### Strategy Planner Agent
- Creates campaign strategies
- Generates Mermaid diagrams
- Plans campaign phases
- Maintains campaign memory

### Content Creator Agent
- Generates A/B content variants
- Optimized for engagement
- Platform-specific formatting
- Hook and reasoning for each variant

### X Platform Agent
- Posts and schedules tweets
- Validates tweet format
- Optimizes posting times
- Handles A/B variant posting

### Metrics Analyzer Agent
- Analyzes tweet performance
- Compares A/B variants
- Provides platform insights
- Recommends optimizations

## Support

For issues or questions:
1. Check the full [README.md](README.md)
2. Review the [demo.py](demo.py) examples
3. Open an issue on GitHub

---

Built for the AI Atlanta Hackathon 🚀
