"""
State management for multi-agent system.
Provides in-memory state storage for campaigns, agent memory, and conversation history.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class CampaignPhase(str, Enum):
    """Campaign phase enumeration"""
    PLANNING = "planning"
    CONTENT_CREATION = "content_creation"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ANALYZING = "analyzing"
    COMPLETED = "completed"


@dataclass
class ContentVariant:
    """Represents a single content variant (A or B)"""
    variant_id: str
    content: str
    platform: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Post:
    """Represents a post with A/B variants"""
    post_id: str
    variants: List[ContentVariant]
    campaign_id: str
    phase: str
    status: str = "draft"  # draft, scheduled, published, analyzed
    selected_variant: Optional[str] = None  # Which variant was chosen
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Campaign:
    """Represents a marketing campaign"""
    campaign_id: str
    name: str
    description: str
    phase: CampaignPhase = CampaignPhase.PLANNING
    posts: List[Post] = field(default_factory=list)
    strategy: Optional[str] = None  # Mermaid diagram
    insights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMemory:
    """Memory storage for individual agents"""
    agent_name: str
    context: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)


class AgentState:
    """
    In-memory state manager for the multi-agent system.
    Stores campaigns, agent memories, and conversation history.
    """

    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.agent_memories: Dict[str, AgentMemory] = {}
        self.conversation_history: List[Dict[str, Any]] = []

    def create_campaign(self, campaign_id: str, name: str, description: str) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            description=description
        )
        self.campaigns[campaign_id] = campaign
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID"""
        return self.campaigns.get(campaign_id)

    def update_campaign_phase(self, campaign_id: str, phase: CampaignPhase):
        """Update campaign phase"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id].phase = phase
            self.campaigns[campaign_id].updated_at = datetime.now()

    def add_post_to_campaign(self, campaign_id: str, post: Post):
        """Add a post to a campaign"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id].posts.append(post)
            self.campaigns[campaign_id].updated_at = datetime.now()

    def update_campaign_strategy(self, campaign_id: str, strategy: str):
        """Update campaign strategy (Mermaid diagram)"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id].strategy = strategy
            self.campaigns[campaign_id].updated_at = datetime.now()

    def add_campaign_insight(self, campaign_id: str, insight: str):
        """Add insight to campaign"""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id].insights.append(insight)
            self.campaigns[campaign_id].updated_at = datetime.now()

    def get_agent_memory(self, agent_name: str) -> AgentMemory:
        """Get or create agent memory"""
        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = AgentMemory(agent_name=agent_name)
        return self.agent_memories[agent_name]

    def update_agent_memory(self, agent_name: str, context: Dict[str, Any]):
        """Update agent memory context"""
        memory = self.get_agent_memory(agent_name)
        memory.context.update(context)
        memory.updated_at = datetime.now()

    def add_to_agent_history(self, agent_name: str, entry: Dict[str, Any]):
        """Add entry to agent history"""
        memory = self.get_agent_memory(agent_name)
        memory.history.append({
            **entry,
            "timestamp": datetime.now().isoformat()
        })
        memory.updated_at = datetime.now()

    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history

    def clear_state(self):
        """Clear all state (useful for testing)"""
        self.campaigns.clear()
        self.agent_memories.clear()
        self.conversation_history.clear()


# Global state instance
state = AgentState()
