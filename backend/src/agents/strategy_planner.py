"""
Strategy Planner Agent
Creates GTM strategies and generates Mermaid diagrams with structured phases.
Converted to agent pattern with structured output.
"""

import os
from typing import Dict, Any, List
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

    def _get_system_prompt(self, regeneration_mode: bool = False) -> str:
        """Get the system prompt for strategy planning with strict format requirements"""
        if regeneration_mode:
            return self._get_regeneration_system_prompt()

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

5. LIMITS
- Limit to 3 nodes per phase maximum
- Node of same phase should not be connected to each other. Instead, connect to the following phases.

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

    def _get_regeneration_system_prompt(self) -> str:
        """Get the system prompt for strategy regeneration from a specific phase"""
        return """You are an expert GTM (Go-To-Market) strategist specializing in SaaS products and technical founders.

Your task is to REGENERATE a marketing strategy from a specific phase onwards, while preserving existing posts from earlier phases.

CRITICAL REQUIREMENTS - YOU MUST FOLLOW EXACTLY:

1. PHASE STRUCTURE:
   - You will receive existing posts from Phase 1 to Phase N-1
   - You must generate NEW strategy for Phase N, Phase N+1, etc. up to Phase 3 (or more if needed)
   - Existing phases will be labeled "(Existing)" in subgraphs
   - New phases will be labeled "(New)" in subgraphs

2. MERMAID FORMAT (EXACT SYNTAX REQUIRED):
   - Start with: graph TB
   - For existing phases: Use subgraph "Phase X (Existing)"
   - For new phases: Use subgraph "Phase X (New)"
   - Node IDs: Use existing node IDs (e.g., NODE1, NODE2) for old posts
   - New nodes: Continue sequential numbering (e.g., NODE5, NODE6, NODE7)
   - Custom node format: NODEX[<title>Title Text</title><description>Description Text</description>]
   - Include connections between nodes using arrows: -->

3. CUSTOM NODE FORMAT (REQUIRED):
   Each node MUST contain both title and description tags:
   - <title>: Short action item (3-5 words)
   - <description>: Brief explanation (5-10 words)

4. CONNECTIONS (MANY-TO-MANY SUPPORT):
   - Connect existing phase nodes TO new phase nodes based on content relevance
   - Support BRANCHING: One old node can connect to MULTIPLE new nodes
   - Support MERGING: Multiple old nodes can connect to ONE new node
   - Use format: NODE1 --> NODE5 (old to new)
   - Nodes within the same phase should NOT be connected to each other
   - Analyze the content, goals, and context to determine logical connections

5. NODES PER PHASE:
   - Generate 2-5 nodes per NEW phase (not limited to 3)
   - More nodes allow for richer strategies and better many-to-many connections

EXAMPLE OUTPUT FORMAT:
```
graph TB
    subgraph "Phase 1 (Existing)"
        NODE1[<title>Old Post 1</title><description>Existing awareness post</description>]
        NODE2[<title>Old Post 2</title><description>Existing community post</description>]
    end
    subgraph "Phase 2 (New)"
        NODE3[<title>New Post 1</title><description>Launch announcement</description>]
        NODE4[<title>New Post 2</title><description>Feature highlight</description>]
        NODE5[<title>New Post 3</title><description>Demo showcase</description>]
    end
    subgraph "Phase 3 (New)"
        NODE6[<title>A/B Testing</title><description>Test messaging variants</description>]
        NODE7[<title>Content Series</title><description>Technical blog posts</description>]
    end
    NODE1 --> NODE3
    NODE1 --> NODE4
    NODE2 --> NODE4
    NODE2 --> NODE5
    NODE3 --> NODE6
    NODE4 --> NODE6
    NODE5 --> NODE7
```

CONNECTION LOGIC:
- Awareness posts (Phase 1) → Launch posts (Phase 2)
- Community posts (Phase 1) → Feature highlights (Phase 2)
- Launch posts (Phase 2) → Growth/optimization posts (Phase 3)
- Multiple paths can converge or diverge based on strategy

STRATEGY GUIDELINES:
- Analyze existing posts to understand campaign direction
- Generate new posts that build upon existing foundation
- Create natural progression from existing content to new content
- Phase 1 (Pre-Launch): Community building, teasers, early awareness, waitlist
- Phase 2 (Launch): ProductHunt, official announcements, press, launch offers
- Phase 3 (Growth): Content marketing, A/B testing, optimization, scaling, partnerships

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

    def execute_from_phase(
        self,
        phase_num: int,
        existing_posts: List[Dict[str, Any]],
        product_description: str,
        gtm_goals: str,
        new_direction: str
    ) -> StrategyOutput:
        """
        Execute strategy regeneration from a specific phase onwards.

        Args:
            phase_num: Phase number to start regeneration from (e.g., 2 means regenerate Phase 2 and onwards)
            existing_posts: List of existing posts from Phase 1 to Phase (phase_num - 1)
                           Each post should have: {post_id, title, description, phase, node_id}
            product_description: Description of the product to market
            gtm_goals: GTM goals and objectives
            new_direction: New direction or prompt for regeneration

        Returns:
            StrategyOutput containing the regenerated Mermaid diagram with existing and new phases
        """
        # Create a regeneration agent with modified system prompt
        regeneration_agent = create_agent(
            self.model,
            tools=[],
            system_prompt=self._get_system_prompt(regeneration_mode=True)
        )

        # Format existing posts for the prompt
        existing_posts_text = self._format_existing_posts(existing_posts)

        # Build the user request
        user_request = f"""Regenerate GTM strategy from Phase {phase_num} onwards.

Product: {product_description}

GTM Goals: {gtm_goals}

New Direction: {new_direction}

EXISTING POSTS (Phase 1 to Phase {phase_num - 1}):
{existing_posts_text}

INSTRUCTIONS:
1. Include ALL existing posts in their original phases with "(Existing)" label
2. Generate NEW posts for Phase {phase_num}, Phase {phase_num + 1}, etc. up to Phase 3 (or more if needed)
3. Create many-to-many connections FROM existing posts TO new posts based on content relevance
4. Support branching (1 old → many new) and merging (many old → 1 new)
5. Generate 2-5 nodes per new phase
6. Follow the new direction: {new_direction}

Generate the complete Mermaid diagram with both existing and new phases."""

        # Invoke the regeneration agent
        result = regeneration_agent.invoke({
            "messages": [{"role": "user", "content": user_request}]
        })

        # Extract diagram from agent response
        diagram_content = self._extract_diagram(result)

        # Return structured output
        return StrategyOutput(diagram=diagram_content)

    def _format_existing_posts(self, existing_posts: List[Dict[str, Any]]) -> str:
        """
        Format existing posts into a readable text format for the prompt.

        Args:
            existing_posts: List of existing posts with metadata

        Returns:
            Formatted string representation of existing posts
        """
        if not existing_posts:
            return "No existing posts."

        # Group posts by phase
        posts_by_phase = {}
        for post in existing_posts:
            phase = post.get('phase', 'Phase 1')
            if phase not in posts_by_phase:
                posts_by_phase[phase] = []
            posts_by_phase[phase].append(post)

        # Format output
        formatted_text = []
        for phase in sorted(posts_by_phase.keys()):
            formatted_text.append(f"\n{phase}:")
            for post in posts_by_phase[phase]:
                node_id = post.get('node_id', 'UNKNOWN')
                title = post.get('title', 'Untitled')
                description = post.get('description', 'No description')
                formatted_text.append(f"  - {node_id}: {title}")
                formatted_text.append(f"    Description: {description}")

        return "\n".join(formatted_text)

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
    import sys

    # Example: Create a strategy
    agent = create_strategy_planner()

    if len(sys.argv) > 1 and sys.argv[1] == "--regenerate":
        # Test regeneration from Phase 2
        print("Testing strategy regeneration from Phase 2...\n")

        # Mock existing posts from Phase 1
        existing_posts = [
            {
                "node_id": "NODE1",
                "post_id": "post_001",
                "title": "Demo video on X",
                "description": "Build hype with demo video",
                "phase": "Phase 1"
            },
            {
                "node_id": "NODE2",
                "post_id": "post_002",
                "title": "Community engagement",
                "description": "Post in relevant subreddits",
                "phase": "Phase 1"
            }
        ]

        result = agent.execute_from_phase(
            phase_num=2,
            existing_posts=existing_posts,
            product_description="Janus - AI-powered GTM OS that automates marketing for technical founders",
            gtm_goals="Launch product and acquire first 100 users in 4 weeks",
            new_direction="Focus on ProductHunt launch with heavy emphasis on developer communities and technical content. Create multiple parallel launch strategies."
        )

        print("Regenerated Strategy Diagram (from Phase 2):")
        print("=" * 60)
        print(result.diagram)
        print("=" * 60)
        print(f"\nDiagram type: {type(result).__name__}")
        print(f"Diagram length: {len(result.diagram)} characters")

    else:
        # Original full strategy generation
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
        print("\nTo test regeneration, run: python -m agents.strategy_planner --regenerate")
