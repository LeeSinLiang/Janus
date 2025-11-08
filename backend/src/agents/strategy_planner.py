"""
Strategy Planner Agent
Creates GTM strategies and generates Mermaid diagrams with structured phases.
Converted to agent pattern with structured output.
"""

import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from pydantic import BaseModel, Field


# =====================
# Output Schema
# =====================

class StrategyOutput(BaseModel):
    """Output schema for strategy planning with Mermaid diagram"""
    diagram: str = Field(description="Mermaid diagram representation of the GTM strategy")


# =====================
# Strategy Planner Agent
# =====================

class StrategyPlannerAgent:
    """
    Agent specialized in creating GTM strategies with Mermaid diagrams.
    Uses agent pattern with structured output for diagram generation.
    """

    def __init__(self):
        """Initialize the Strategy Planner Agent with agent pattern."""
        # Get model name from environment variable
        model_name = os.getenv("GEMINI_MODEL_CODE", "gemini-2.5-flash")

        # Create base model with temperature 0 for consistent output
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0
        )

        # Create agent (no tools needed for this use case)
        self.agent = create_agent(
            self.model,
            tools=[],  # No external tools needed
            system_prompt=self._get_system_prompt()
        )

        # Agent name for reference
        self.agent_name = "strategy_planner"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for strategy planning with strict format requirements"""
        return """You are an expert GTM (Go-To-Market) strategist specializing in SaaS products and technical founders.

Your task is to create a phased marketing strategy and generate a Mermaid diagram visualization.

CRITICAL REQUIREMENTS - YOU MUST FOLLOW EXACTLY:

1. EXACTLY 3 PHASES (NO MORE, NO LESS):
   - Phase 1: Pre-launch/Awareness phase
   - Phase 2: Launch phase
   - Phase 3: Post-launch/Growth phase

2. MERMAID FORMAT (EXACT SYNTAX REQUIRED):
   - Start with: graph TB
   - Create 3 subgraphs with exact names: "Phase 1", "Phase 2", "Phase 3"
   - Node IDs: NODE1, NODE2, NODE3, etc. (sequential numbering)
   - Custom node format: NODEX[<title>Title Text</title><description>Description Text</description>]
   - Include connections between nodes using arrows: -->

3. CUSTOM NODE FORMAT (REQUIRED):
   Each node MUST contain both title and description tags:
   - <title>: Short action item (3-5 words)
   - <description>: Brief explanation (5-10 words)

4. CONNECTIONS:
   - Connect nodes within and across phases
   - Show logical flow from Phase 1 → Phase 2 → Phase 3
   - Use format: NODE1 --> NODE2

EXAMPLE OUTPUT FORMAT:
```
graph TB
    subgraph "Phase 1"
        NODE1[<title>Post demo to X</title><description>Build hype with demo video</description>]
        NODE2[<title>Engage communities</title><description>Post in relevant subreddits</description>]
    end
    subgraph "Phase 2"
        NODE3[<title>ProductHunt launch</title><description>Launch on ProductHunt</description>]
        NODE4[<title>Announcement thread</title><description>Post launch thread on X</description>]
    end
    subgraph "Phase 3"
        NODE5[<title>A/B testing</title><description>Test different messaging</description>]
        NODE6[<title>Content marketing</title><description>Publish technical blog posts</description>]
    end
    NODE1 --> NODE2
    NODE2 --> NODE3
    NODE3 --> NODE4
    NODE4 --> NODE5
    NODE5 --> NODE6
```

STRATEGY GUIDELINES:
- Phase 1 (Pre-Launch): Community building, teasers, early awareness, waitlist
- Phase 2 (Launch): ProductHunt, official announcements, press, launch offers
- Phase 3 (Growth): Content marketing, A/B testing, optimization, scaling, partnerships

BEST PRACTICES FOR TECHNICAL FOUNDERS:
- Focus on authentic, technical-first content
- Leverage developer communities (X, Reddit, HackerNews)
- Emphasize ProductHunt for visibility
- Use data-driven approaches (A/B testing, metrics)
- Build in public when possible

OUTPUT REQUIREMENTS:
Return ONLY the Mermaid diagram code. Do NOT include markdown code blocks, explanations, or additional text.
Start directly with "graph TB" and include the complete diagram."""

    def execute(self, product_description: str, gtm_goals: str) -> StrategyOutput:
        """
        Execute strategy planning and generate Mermaid diagram.

        Args:
            product_description: Description of the product to market
            gtm_goals: GTM goals and objectives

        Returns:
            StrategyOutput containing the Mermaid diagram
        """
        # Build the user request
        user_request = f"""Create a GTM strategy for:

Product: {product_description}

GTM Goals: {gtm_goals}

Generate a Mermaid diagram following the required format with exactly 3 phases."""

        # Invoke the agent
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": user_request}]
        })

        # Extract diagram from agent response
        diagram_content = self._extract_diagram(result)

        # Return structured output
        return StrategyOutput(diagram=diagram_content)

    def _extract_diagram(self, agent_result: Dict[str, Any]) -> str:
        """
        Extract the Mermaid diagram from agent result.

        Args:
            agent_result: Result from agent invocation

        Returns:
            Cleaned Mermaid diagram string
        """
        # Get the last message from the agent
        messages = agent_result.get("messages", [])
        if not messages:
            return "graph TB\n    NODE1[<title>Error</title><description>No output generated</description>]"

        last_message = messages[-1]

        # Extract content
        if hasattr(last_message, 'content'):
            content = last_message.content
        else:
            content = str(last_message)

        # Clean up the content (remove markdown code blocks if present)
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```mermaid"):
            content = content.replace("```mermaid", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        return content


# =====================
# Convenience Functions
# =====================

def create_strategy_planner() -> StrategyPlannerAgent:
    """
    Factory function to create a Strategy Planner Agent.

    Returns:
        Initialized StrategyPlannerAgent
    """
    return StrategyPlannerAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Create a strategy
    agent = create_strategy_planner()

    result = agent.execute(
        product_description="Janus - AI-powered GTM OS that automates marketing for technical founders",
        gtm_goals="Launch product and acquire first 100 users in 4 weeks"
    )

    print("Generated Strategy Diagram:")
    print("=" * 60)
    print(result.diagram)
    print("=" * 60)
    print(f"\nDiagram type: {type(result).__name__}")
    print(f"Diagram length: {len(result.diagram)} characters")
