"""
Mini Strategy Agent
Generates new post (title, description, phase) based on existing posts and user modifications.
Used for creating follow-up posts in a campaign flow.
"""

import os
from typing import Dict, Any, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from pydantic import BaseModel, Field


# =====================
# Output Schema
# =====================

class MiniStrategyOutput(BaseModel):
    """Output schema for mini strategy planning"""
    title: str = Field(description="Short title for the new post (3-5 words)")
    description: str = Field(description="Description of the post content and purpose (10-20 words)")
    phase: Literal["Phase 1", "Phase 2", "Phase 3"] = Field(
        description="The phase this post belongs to (can only be current or next phase from selected posts)"
    )


# =====================
# Mini Strategy Agent
# =====================

class MiniStrategyAgent:
    """
    Agent specialized in creating new posts based on existing campaign posts.
    Generates title, description, and determines appropriate phase.
    """

    def __init__(self):
        """Initialize the Mini Strategy Agent with agent pattern."""
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
        self.agent_name = "mini_strategy_agent"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for generating new post from selected posts"""
        return """You are an expert GTM strategist specializing in creating follow-up marketing posts within existing campaigns.

Your task is to generate a NEW post that builds upon or follows selected posts in a campaign.

CONTEXT YOU WILL RECEIVE:
1. Selected Posts: The posts that the new post will follow (title, description, content variants)
2. Campaign Strategy: Overall Mermaid diagram showing campaign structure
3. User Prompt: Specific modifications or direction for the new post
4. Phase Context: Current phases of selected posts

YOUR JOB:
Generate a new post (title, description, phase) that:
- FOLLOWS the selected posts in the campaign flow
- ALIGNS with the overall campaign strategy
- INCORPORATES the user's requested modifications
- FITS logically in the campaign progression

PHASE SELECTION RULES:
- You can ONLY select a phase that is the CURRENT or NEXT phase relative to selected posts
- If selected posts are in "Phase 1", you can choose "Phase 1" or "Phase 2"
- If selected posts are in "Phase 2", you can choose "Phase 2" or "Phase 3"
- If selected posts are in "Phase 3", you can only choose "Phase 3"
- The new post typically belongs to the SAME or NEXT phase (progression)

OUTPUT REQUIREMENTS:
- Title: Short, actionable title (3-5 words) - e.g., "Post demo video", "Engage Reddit communities"
- Description: Brief explanation of what this post does (10-20 words)
- Phase: Must be current or next phase from selected posts

STRATEGY GUIDELINES:
- Phase 1 (Pre-Launch): Community building, teasers, early awareness
- Phase 2 (Launch): ProductHunt, announcements, press releases
- Phase 3 (Growth): Content marketing, A/B testing, optimization, partnerships

BEST PRACTICES:
- Ensure the new post creates a logical progression from selected posts
- Consider the campaign's overall narrative and goals
- Make titles actionable and specific
- Keep descriptions focused on purpose and outcome"""

    def execute(
        self,
        selected_posts_context: str,
        campaign_strategy: str,
        user_prompt: str,
        current_phases: str
    ) -> MiniStrategyOutput:
        """
        Generate a new post based on selected posts and user modifications.

        Args:
            selected_posts_context: Context about selected posts (titles, descriptions, variants)
            campaign_strategy: Overall campaign strategy (Mermaid diagram or summary)
            user_prompt: User's requested modifications or direction
            current_phases: Information about current phases of selected posts

        Returns:
            MiniStrategyOutput containing title, description, and phase
        """
        # Build the user request
        user_request = f"""Create a new post that follows these selected posts:

{selected_posts_context}

Campaign Strategy Context:
{campaign_strategy}

Phase Information:
{current_phases}

User's Request:
{user_prompt}

Generate a new post (title, description, phase) that follows logically from the selected posts and incorporates the user's request."""

        # Invoke the agent
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": user_request}]
        })

        # Extract output from agent response
        output = self._extract_output(result)

        return output

    def _extract_output(self, agent_result: Dict[str, Any]) -> MiniStrategyOutput:
        """
        Extract the MiniStrategyOutput from agent result.

        Args:
            agent_result: Result from agent invocation

        Returns:
            MiniStrategyOutput object
        """
        # Check for structured_response key (LangChain standard)
        if "structured_response" in agent_result:
            if isinstance(agent_result["structured_response"], MiniStrategyOutput):
                return agent_result["structured_response"]

        # Get messages array
        messages = agent_result.get("messages", [])
        if not messages:
            return MiniStrategyOutput(
                title="Error: No output",
                description="Failed to generate post",
                phase="Phase 1"
            )

        last_message = messages[-1]

        # Check if message is already MiniStrategyOutput
        if isinstance(last_message, MiniStrategyOutput):
            return last_message

        # Check if message has content that is MiniStrategyOutput
        if hasattr(last_message, 'content'):
            content = last_message.content
            if isinstance(content, MiniStrategyOutput):
                return content
            # Try to parse if it's a dict
            if isinstance(content, dict):
                return MiniStrategyOutput(**content)

        # Fallback error
        return MiniStrategyOutput(
            title="Error: Invalid output",
            description="Agent did not return valid structured output",
            phase="Phase 1"
        )


# =====================
# Convenience Functions
# =====================

def create_mini_strategy_agent() -> MiniStrategyAgent:
    """
    Factory function to create a Mini Strategy Agent.

    Returns:
        Initialized MiniStrategyAgent
    """
    return MiniStrategyAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Generate a new post based on selected posts
    agent = create_mini_strategy_agent()

    selected_context = """Selected Posts:
1. Title: "Post demo video"
   Description: "Share product demo on X to build initial awareness"
   Phase: Phase 1
   Variant A: "Just launched Janus - AI GTM OS for founders. Check out our demo 🚀"
   Variant B: "Building in public: Here's how Janus automates your marketing strategy 🎯"

2. Title: "Engage Reddit communities"
   Description: "Post in r/SaaS and r/startups to gather feedback"
   Phase: Phase 1
   Variant A: "We built an AI tool that plans your entire GTM strategy. Thoughts?"
   Variant B: "Technical founders: Stop wasting time on marketing. Try Janus."""

    campaign_strategy = """Campaign focuses on technical founder audience.
Phase 1: Building awareness through X and Reddit
Phase 2: ProductHunt launch
Phase 3: Content marketing and partnerships"""

    user_prompt = "Create a follow-up post that asks for beta testers"

    phases_info = "Selected posts are in Phase 1. You can choose Phase 1 or Phase 2."

    result = agent.execute(
        selected_posts_context=selected_context,
        campaign_strategy=campaign_strategy,
        user_prompt=user_prompt,
        current_phases=phases_info
    )

    print("Generated New Post:")
    print("=" * 60)
    print(f"Title: {result.title}")
    print(f"Description: {result.description}")
    print(f"Phase: {result.phase}")
    print("=" * 60)
