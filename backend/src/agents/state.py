"""
State management for multi-agent system.
Provides database-backed state storage using Django ORM for campaigns, agent memory, and conversation history.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# Import Django models - these replace the dataclasses
from .models import Campaign, Post, ContentVariant, AgentMemory, ConversationMessage


class CampaignPhase(str, Enum):
    """Campaign phase enumeration - matches Django model choices"""
    PLANNING = "planning"
    CONTENT_CREATION = "content_creation"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ANALYZING = "analyzing"
    COMPLETED = "completed"


class AgentState:
    """
    Database-backed state manager for the multi-agent system.
    Stores campaigns, agent memories, and conversation history in Django database.

    This replaces the previous in-memory storage with persistent database storage.
    """

    def __init__(self):
        """Initialize state manager - no in-memory storage needed"""
        pass

    def create_campaign(self, campaign_id: str, name: str, description: str) -> Campaign:
        """
        Create a new campaign in the database.

        Args:
            campaign_id: Unique campaign identifier
            name: Campaign name
            description: Campaign description

        Returns:
            Campaign model instance
        """
        campaign, created = Campaign.objects.get_or_create(
            campaign_id=campaign_id,
            defaults={
                'name': name,
                'description': description,
                'phase': 'planning'
            }
        )
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """
        Get a campaign by ID from database.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Campaign model instance or None if not found
        """
        try:
            return Campaign.objects.get(campaign_id=campaign_id)
        except Campaign.DoesNotExist:
            return None

    def update_campaign_phase(self, campaign_id: str, phase: CampaignPhase):
        """
        Update campaign phase in database.

        Args:
            campaign_id: Campaign identifier
            phase: New campaign phase
        """
        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            campaign.phase = phase.value if isinstance(phase, Enum) else phase
            campaign.save(update_fields=['phase', 'updated_at'])
        except Campaign.DoesNotExist:
            pass

    def add_post_to_campaign(self, campaign_id: str, post_data: Dict[str, Any]):
        """
        Add a post to a campaign in database.

        Args:
            campaign_id: Campaign identifier
            post_data: Dictionary containing post data with variants
        """
        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)

            # Create the Post
            post = Post.objects.create(
                post_id=post_data.get('post_id', f'post_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
                campaign=campaign,
                phase=post_data.get('phase', ''),
                status=post_data.get('status', 'draft'),
                selected_variant=post_data.get('selected_variant'),
                metrics=post_data.get('metrics', {})
            )

            # Create ContentVariants if provided
            variants = post_data.get('variants', [])
            for variant_data in variants:
                ContentVariant.objects.create(
                    variant_id=variant_data.get('variant_id', 'A'),
                    post=post,
                    content=variant_data.get('content', ''),
                    platform=variant_data.get('platform', 'x'),
                    metadata=variant_data.get('metadata', {})
                )

            # Touch the campaign to update its timestamp
            campaign.save(update_fields=['updated_at'])

        except Campaign.DoesNotExist:
            pass

    def update_campaign_strategy(self, campaign_id: str, strategy: str):
        """
        Update campaign strategy (Mermaid diagram) in database.

        Args:
            campaign_id: Campaign identifier
            strategy: Mermaid diagram string
        """
        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            campaign.strategy = strategy
            campaign.save(update_fields=['strategy', 'updated_at'])
        except Campaign.DoesNotExist:
            pass

    def add_campaign_insight(self, campaign_id: str, insight: str):
        """
        Add insight to campaign in database.

        Args:
            campaign_id: Campaign identifier
            insight: Insight text to add
        """
        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            campaign.add_insight(insight)  # Uses model method
        except Campaign.DoesNotExist:
            pass

    def get_agent_memory(self, agent_name: str) -> AgentMemory:
        """
        Get or create agent memory from database.

        Args:
            agent_name: Name of the agent

        Returns:
            AgentMemory model instance
        """
        memory, created = AgentMemory.objects.get_or_create(
            agent_name=agent_name,
            defaults={
                'context': {},
                'history': []
            }
        )
        return memory

    def update_agent_memory(self, agent_name: str, context: Dict[str, Any]):
        """
        Update agent memory context in database.

        Args:
            agent_name: Name of the agent
            context: Context dictionary to merge
        """
        memory = self.get_agent_memory(agent_name)
        memory.update_context(context)  # Uses model method

    def add_to_agent_history(self, agent_name: str, entry: Dict[str, Any]):
        """
        Add entry to agent history in database.

        Args:
            agent_name: Name of the agent
            entry: History entry dictionary
        """
        memory = self.get_agent_memory(agent_name)
        memory.add_to_history(entry)  # Uses model method

    def add_to_conversation(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        campaign_id: Optional[str] = None
    ):
        """
        Add message to conversation history in database.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata dictionary
            campaign_id: Optional campaign identifier to link message to
        """
        campaign = None
        if campaign_id:
            try:
                campaign = Campaign.objects.get(campaign_id=campaign_id)
            except Campaign.DoesNotExist:
                pass

        ConversationMessage.objects.create(
            role=role,
            content=content,
            metadata=metadata or {},
            campaign=campaign
        )

    def get_conversation_history(
        self,
        limit: Optional[int] = None,
        campaign_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from database.

        Args:
            limit: Optional limit on number of messages
            campaign_id: Optional campaign filter

        Returns:
            List of conversation message dictionaries
        """
        queryset = ConversationMessage.objects.all()

        if campaign_id:
            queryset = queryset.filter(campaign__campaign_id=campaign_id)

        if limit:
            queryset = queryset.order_by('-created_at')[:limit]
            # Reverse to get chronological order
            messages = list(reversed(list(queryset)))
        else:
            messages = list(queryset)

        # Convert to dictionary format
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    def clear_state(self):
        """
        Clear all state from database (useful for testing).
        WARNING: This deletes all data!
        """
        Campaign.objects.all().delete()
        AgentMemory.objects.all().delete()
        ConversationMessage.objects.all().delete()
        Post.objects.all().delete()
        ContentVariant.objects.all().delete()


# Global state instance - now uses database instead of memory
state = AgentState()
