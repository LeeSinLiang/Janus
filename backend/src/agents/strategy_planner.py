"""
Strategy Planner Agent
Creates marketing strategies, campaigns, and generates Mermaid diagrams.
Maintains campaign context and memory.
"""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from .state import state, Campaign, CampaignPhase
import os
from datetime import datetime
import uuid


# =====================
# Output Schemas
# =====================

class CampaignPhaseNode(BaseModel):
    """Schema for a campaign phase"""
    phase_id: str = Field(description="Unique phase identifier")
    phase_name: str = Field(description="Phase name (e.g., 'Awareness', 'Launch', 'Growth')")
    duration: str = Field(description="Duration of this phase")
    channels: List[str] = Field(description="Marketing channels for this phase")
    objectives: List[str] = Field(description="Key objectives")
    content_themes: List[str] = Field(description="Content themes and topics")


class StrategyOutput(BaseModel):
    """Schema for strategy planning output"""
    campaign_name: str = Field(description="Campaign name")
    campaign_goal: str = Field(description="Overall campaign goal")
    target_audience: str = Field(description="Target audience description")
    phases: List[CampaignPhaseNode] = Field(description="Campaign phases")
    mermaid_diagram: str = Field(description="Mermaid diagram representation")
    key_metrics: List[str] = Field(description="Key metrics to track")
    success_criteria: str = Field(description="What defines success")


# =====================
# Strategy Planner Agent
# =====================

class StrategyPlannerAgent:
    """
    Agent specialized in creating marketing strategies and campaign plans.
    Generates Mermaid diagrams for visualization and maintains campaign memory.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.6):
        """
        Initialize the Strategy Planner Agent.

        Args:
            model_name: Google Gemini model to use
            temperature: Moderate temperature for creative yet structured planning
        """
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Set up structured output parser
        self.parser = JsonOutputParser(pydantic_object=StrategyOutput)

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{request}")
        ])

        # Create the chain
        self.chain = self.prompt | self.model | self.parser

        # Agent name for memory storage
        self.agent_name = "strategy_planner"

    def _get_system_prompt(self) -> str:
        """Get the system prompt for strategy planning"""
        return """You are an expert marketing strategist specializing in go-to-market strategies for SaaS products and technical startups.

Your task is to create comprehensive, phased marketing campaigns with clear visualization.

STRATEGY FRAMEWORK:
1. Understand the product, audience, and goals
2. Break down the campaign into phases (typically 3-5 phases):
   - Pre-Launch/Awareness
   - Launch
   - Growth/Scaling
   - Retention/Optimization
3. For each phase, define:
   - Objectives
   - Marketing channels
   - Content themes
   - Duration
   - Success metrics
4. Generate a Mermaid diagram showing the campaign flow

MERMAID DIAGRAM FORMAT:
Create a flowchart showing:
- Campaign phases as nodes
- Channels within each phase
- Flow between phases
- Decision points (if applicable)

Example structure:
```mermaid
graph TD
    A[Campaign Start] --> B[Phase 1: Awareness]
    B --> B1[X Platform Posts]
    B --> B2[ProductHunt Teaser]
    B1 --> C[Phase 2: Launch]
    B2 --> C
    C --> C1[ProductHunt Launch]
    C --> C2[X Announcement Thread]
    C1 --> D[Phase 3: Growth]
    C2 --> D
    D --> D1[Content Marketing]
    D --> D2[A/B Testing]
```

TARGET AUDIENCE CONSIDERATIONS:
- Technical founders: Prefer data-driven, practical content
- Developers: Value technical depth and authenticity
- Startup owners: Care about ROI and efficiency

OUTPUT FORMAT:
Return a JSON object with this structure:
{
  "campaign_name": "string",
  "campaign_goal": "string",
  "target_audience": "string",
  "phases": [
    {
      "phase_id": "phase_1",
      "phase_name": "Awareness",
      "duration": "2 weeks",
      "channels": ["X", "ProductHunt"],
      "objectives": ["Build anticipation", "Gather early feedback"],
      "content_themes": ["Problem statement", "Sneak peeks"]
    }
  ],
  "mermaid_diagram": "graph TD\\n    A[Start] --> B[Phase 1]",
  "key_metrics": ["engagement_rate", "follower_growth", "signups"],
  "success_criteria": "string describing success"
}

Be strategic, data-driven, and create actionable plans."""

    def create_strategy(
        self,
        product_info: str,
        campaign_goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a marketing strategy and campaign plan.

        Args:
            product_info: Information about the product
            campaign_goal: Main goal of the campaign
            context: Optional context (budget, timeline, constraints)

        Returns:
            Strategy output with phases and Mermaid diagram
        """
        request = f"""Create a marketing strategy for:

Product: {product_info}
Campaign Goal: {campaign_goal}"""

        if context:
            request += f"\n\nAdditional Context: {context}"

        request += "\n\nGenerate a phased campaign plan with a Mermaid diagram."

        # Generate strategy
        result = self.chain.invoke({"request": request})

        # Store in memory
        campaign_id = str(uuid.uuid4())
        self._save_to_memory(campaign_id, result)

        return {
            **result,
            "campaign_id": campaign_id
        }

    def update_strategy(
        self,
        campaign_id: str,
        updates: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing strategy based on new information or metrics.

        Args:
            campaign_id: The campaign to update
            updates: Description of what to update
            metrics: Optional metrics to inform updates

        Returns:
            Updated strategy
        """
        # Get existing campaign from memory
        campaign = state.get_campaign(campaign_id)

        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        request = f"""Update this marketing strategy:

Current Campaign: {campaign.name}
Current Strategy: {campaign.strategy if campaign.strategy else 'Not yet defined'}

Updates needed: {updates}"""

        if metrics:
            request += f"\n\nCurrent Metrics: {metrics}"

        request += "\n\nGenerate an updated strategy and Mermaid diagram."

        # Generate updated strategy
        result = self.chain.invoke({"request": request})

        # Update memory
        self._save_to_memory(campaign_id, result)

        return {
            **result,
            "campaign_id": campaign_id
        }

    def create_phase_plan(
        self,
        campaign_id: str,
        phase_name: str,
        duration: str
    ) -> Dict[str, Any]:
        """
        Create a detailed plan for a specific campaign phase.

        Args:
            campaign_id: The campaign this phase belongs to
            phase_name: Name of the phase
            duration: Duration of the phase

        Returns:
            Detailed phase plan
        """
        campaign = state.get_campaign(campaign_id)

        request = f"""Create a detailed plan for this campaign phase:

Campaign: {campaign.name if campaign else 'Unknown'}
Phase: {phase_name}
Duration: {duration}

Provide:
1. Daily/weekly content calendar
2. Specific post ideas
3. Channel-specific tactics
4. Success metrics
5. Contingency plans"""

        result = self.chain.invoke({"request": request})

        # Add to campaign insights
        if campaign:
            state.add_campaign_insight(
                campaign_id,
                f"Phase plan created for {phase_name}: {result.get('mermaid_diagram', '')}"
            )

        return result

    def generate_mermaid_diagram(
        self,
        campaign_structure: Dict[str, Any]
    ) -> str:
        """
        Generate a Mermaid diagram from campaign structure.

        Args:
            campaign_structure: Campaign phases and structure

        Returns:
            Mermaid diagram string
        """
        request = f"""Generate a Mermaid flowchart diagram for this campaign structure:

{campaign_structure}

Create a clear, visual flowchart showing:
- All phases
- Channels within each phase
- Flow between phases
- Decision points

Return ONLY the Mermaid diagram code (starting with 'graph TD')."""

        # Use the model directly for this simpler task
        response = self.model.invoke(request)

        # Extract mermaid code from response
        mermaid_code = response.content if hasattr(response, 'content') else str(response)

        return mermaid_code.strip()

    def _save_to_memory(self, campaign_id: str, strategy_data: Dict[str, Any]):
        """
        Save strategy to memory.

        Args:
            campaign_id: Campaign identifier
            strategy_data: Strategy data to save
        """
        # Update or create campaign in state
        campaign = state.get_campaign(campaign_id)

        if not campaign:
            # Create new campaign
            campaign = state.create_campaign(
                campaign_id=campaign_id,
                name=strategy_data.get("campaign_name", "Unnamed Campaign"),
                description=strategy_data.get("campaign_goal", "")
            )

        # Update campaign with strategy
        state.update_campaign_strategy(
            campaign_id,
            strategy_data.get("mermaid_diagram", "")
        )

        # Update agent memory
        state.update_agent_memory(
            self.agent_name,
            {
                "last_campaign": campaign_id,
                "last_update": datetime.now().isoformat()
            }
        )

        # Add to agent history
        state.add_to_agent_history(
            self.agent_name,
            {
                "action": "strategy_created",
                "campaign_id": campaign_id,
                "campaign_name": strategy_data.get("campaign_name", "")
            }
        )

    def get_campaign_from_memory(self, campaign_id: str) -> Optional[Campaign]:
        """
        Retrieve campaign from memory.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Campaign object if found
        """
        return state.get_campaign(campaign_id)

    def get_agent_memory(self) -> Dict[str, Any]:
        """
        Get agent's memory context.

        Returns:
            Agent memory data
        """
        memory = state.get_agent_memory(self.agent_name)
        return {
            "context": memory.context,
            "recent_history": memory.history[-5:] if memory.history else []
        }


# =====================
# Convenience Functions
# =====================

def create_strategy_planner(api_key: Optional[str] = None) -> StrategyPlannerAgent:
    """
    Factory function to create a Strategy Planner Agent.

    Args:
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Initialized StrategyPlannerAgent
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    return StrategyPlannerAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Create a strategy
    agent = create_strategy_planner()

    result = agent.create_strategy(
        product_info="Janus - AI-powered GTM OS that automates marketing for technical founders",
        campaign_goal="Launch product and acquire first 100 users",
        context={
            "timeline": "4 weeks",
            "budget": "low",
            "channels": ["X", "ProductHunt"]
        }
    )

    print("Strategy Created:")
    print(f"Campaign: {result['campaign_name']}")
    print(f"Goal: {result['campaign_goal']}")
    print(f"\nPhases ({len(result['phases'])}):")
    for phase in result['phases']:
        print(f"  - {phase['phase_name']}: {phase['duration']}")
    print(f"\nMermaid Diagram:")
    print(result['mermaid_diagram'])
    print(f"\nCampaign ID: {result['campaign_id']}")
