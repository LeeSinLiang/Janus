"""
Janus Multi-Agent System

A multi-agent architecture for AI-powered Go-To-Market (GTM) automation.

Agents:
- OrchestratorAgent: Supervisor that coordinates all sub-agents
- StrategyPlannerAgent: Creates marketing strategies and Mermaid diagrams
- ContentCreatorAgent: Generates A/B content variants
- XPlatformAgent: Handles X (Twitter) posting and scheduling
- MetricsAnalyzerAgent: Analyzes metrics and provides insights

Usage:
    from agents import create_orchestrator

    orchestrator = create_orchestrator()
    result = orchestrator.execute("Create a marketing strategy for my SaaS product")
"""

from .supervisor import OrchestratorAgent, create_orchestrator
from .strategy_planner import StrategyPlannerAgent, create_strategy_planner
from .content_creator import ContentCreatorAgent, create_content_creator
from .x_platform import XPlatformAgent, create_x_platform_agent
from .metrics_analyzer import MetricsAnalyzerAgent, create_metrics_analyzer
from .state import state, AgentState, Campaign, Post, ContentVariant

__all__ = [
    # Main orchestrator
    "OrchestratorAgent",
    "create_orchestrator",
    # Sub-agents
    "StrategyPlannerAgent",
    "create_strategy_planner",
    "ContentCreatorAgent",
    "create_content_creator",
    "XPlatformAgent",
    "create_x_platform_agent",
    "MetricsAnalyzerAgent",
    "create_metrics_analyzer",
    # State management
    "state",
    "AgentState",
    "Campaign",
    "Post",
    "ContentVariant",
]

__version__ = "0.1.0"
