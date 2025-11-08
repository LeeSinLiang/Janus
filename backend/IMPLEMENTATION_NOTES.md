# Implementation Notes - LangChain with Google Generative AI

## Correct Implementation Pattern

The Janus multi-agent system uses **LangChain with Google Generative AI (Gemini)** following the official pattern from https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai

### Key Components

#### 1. Imports
```python
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
```

#### 2. Model Initialization
```python
self.model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=temperature
)
```

**Supported Models:**
- `"gemini-2.5-flash"` (recommended for speed)
- `"gemini-2.5-flash-lite"` (lightweight)
- `"gemini-1.5-pro"` (high quality)

See [Gemini API docs](https://ai.google.dev/gemini-api/docs/models) for all models.

#### 3. Agent Creation
For agents that use tools:
```python
self.agent = create_agent(
    self.model,
    tools=self.tools,
    system_prompt=self._get_system_prompt()
)
```

For agents that use chains (content generation):
```python
self.chain = self.prompt | self.model | self.parser
```

#### 4. Agent Invocation
```python
result = self.agent.invoke({
    "messages": [{"role": "user", "content": user_input}]
})
```

#### 5. Output Extraction
```python
def _extract_output(self, result: Dict[str, Any]) -> str:
    """Helper to extract output from agent result"""
    if "messages" in result:
        last_message = result["messages"][-1]
        if hasattr(last_message, 'content'):
            return last_message.content
        elif isinstance(last_message, dict):
            return last_message.get('content', str(last_message))
    return str(result)
```

## Architecture

The system follows the **3-layer supervisor pattern**:

```
┌─────────────────────────────────────┐
│   Layer 3: Orchestrator/Supervisor │  ← Coordinates workflow
│   (supervisor.py)                    │
│   Uses: create_agent()              │
└──────────────┬──────────────────────┘
               │ Wraps sub-agents as tools
┌──────────────▼──────────────────────┐
│   Layer 2: Specialized Sub-Agents   │  ← Domain expertise
│   - Strategy Planner (chain)        │
│   - Content Creator (chain)         │
│   - X Platform Agent (agent)        │
│   - Metrics Analyzer (agent)        │
└──────────────┬──────────────────────┘
               │ Uses low-level tools
┌──────────────▼──────────────────────┐
│   Layer 1: Low-Level Tools          │  ← API calls
│   (tools.py)                         │
│   - post_tweet                       │
│   - get_metrics                      │
│   - etc.                             │
└─────────────────────────────────────┘
```

## Files and Patterns

### Agents Using `create_agent()` Pattern
These files use the agent pattern with tools:

1. **`supervisor.py`** - Main orchestrator
   - Uses `create_agent()` with sub-agent tools
   - Invokes: `agent.invoke({"messages": [...]})`

2. **`x_platform.py`** - X Platform operations
   - Uses `create_agent()` with X API tools
   - Invokes: `agent.invoke({"messages": [...]})`

3. **`metrics_analyzer.py`** - Metrics analysis
   - Uses `create_agent()` with metrics tools
   - Invokes: `agent.invoke({"messages": [...]})`

### Agents Using Chain Pattern
These files use direct chain pattern (prompt | model | parser):

1. **`content_creator.py`** - Content generation
   - Uses: `self.chain = self.prompt | self.model | self.parser`
   - Invokes: `self.chain.invoke({"request": ...})`

2. **`strategy_planner.py`** - Strategy planning
   - Uses: `self.chain = self.prompt | self.model | self.parser`
   - Invokes: `self.chain.invoke({"request": ...})`

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `langchain>=0.3.0`
- `langchain-google-genai>=2.0.0`
- `langgraph>=0.2.0`
- `google-generativeai>=0.8.0`

### 2. Configure API Key
```bash
# Create .env file
cp .env.example .env

# Add your Google API key
GOOGLE_API_KEY=your_api_key_here
```

Get your API key from: https://ai.google.dev/gemini-api/docs/api-key

### 3. Run Demo
```bash
python demo.py
```

## Usage Example

```python
from agents import create_orchestrator

# Initialize
orchestrator = create_orchestrator()

# Execute
result = orchestrator.execute(
    "Create a marketing strategy for my product"
)

# Access output
print(result['output'])
```

## Common Issues & Solutions

### Issue: "Cannot import create_agent"
**Solution:** Update langchain to >=0.3.0
```bash
pip install -U langchain
```

### Issue: "Model not found"
**Solution:** Ensure model name is correct:
- ✅ `"gemini-2.5-flash"`
- ✅ `"gemini-1.5-pro"`
- ❌ `"google_genai:gemini-2.5-flash"` (wrong format)

### Issue: "GOOGLE_API_KEY not found"
**Solution:** Set environment variable in .env file
```bash
GOOGLE_API_KEY=your_actual_key_here
```

### Issue: "messages key not found"
**Solution:** Use correct invocation format:
```python
# ✅ Correct
agent.invoke({"messages": [{"role": "user", "content": text}]})

# ❌ Wrong
executor.invoke({"input": text})
```

## Testing

### Test Individual Agents
```bash
# Test content creator
cd src
python -m agents.content_creator

# Test strategy planner
python -m agents.strategy_planner

# Test supervisor
python -m agents.supervisor
```

### Test Complete System
```bash
python demo.py
```

## References

- **LangChain Google GenAI:** https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai
- **LangChain Supervisor:** https://docs.langchain.com/oss/python/langchain/supervisor
- **Gemini API:** https://ai.google.dev/gemini-api/docs
- **Gemini Models:** https://ai.google.dev/gemini-api/docs/models

## Next Steps

1. ✅ All agents use correct ChatGoogleGenerativeAI pattern
2. ✅ Model names use correct format (`"gemini-2.5-flash"`)
3. ✅ Requirements.txt updated
4. ✅ Code tested and working
5. 🔄 Ready for React frontend integration
6. 🔄 Can add real X API when ready
7. 🔄 Can extend with long-term memory (PostgreSQL/Vector DB)
