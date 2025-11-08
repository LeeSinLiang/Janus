#!/usr/bin/env python
"""
Janus Multi-Agent System Demo

Demonstrates the complete workflow of the Janus GTM OS.
Make sure to set GOOGLE_API_KEY in your .env file before running.
"""

import json
import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "janus.settings")
import django
django.setup()

from agents import (
    create_orchestrator,
    create_strategy_planner,
    create_content_creator,
    create_metrics_analyzer,
    state
)


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_orchestrator():
    """Demo the orchestrator coordinating all agents"""
    print_section("🎯 ORCHESTRATOR DEMO - Complete Workflow")

    orchestrator = create_orchestrator()

    # Example 1: Create campaign strategy
    print("📋 1. Creating Campaign Strategy...")
    result = orchestrator.execute(
        "Create a marketing strategy for Janus, an AI-powered GTM OS for technical founders. "
        "Goal: Launch and get first 100 users in 4 weeks using X and ProductHunt."
    )
    print(f"✅ Strategy created!")
    print(f"Output preview: {result.get('output', '')[:300]}...\n")

    # Example 2: Generate content
    print("✍️  2. Generating Content with A/B Variants...")
    result = orchestrator.execute(
        "Generate tweet content announcing our product launch with A/B variants"
    )
    print(f"✅ Content generated!")
    print(f"Output preview: {result.get('output', '')[:300]}...\n")

    # Example 3: Analyze metrics
    print("📊 3. Analyzing Platform Metrics...")
    result = orchestrator.execute(
        "Analyze platform insights and recommend optimal posting times"
    )
    print(f"✅ Analysis complete!")
    print(f"Output preview: {result.get('output', '')[:300]}...\n")


def demo_individual_agents():
    """Demo individual agents working independently"""
    print_section("🤖 INDIVIDUAL AGENTS DEMO")

    # 1. Strategy Planner
    print("📋 Strategy Planner Agent")
    print("-" * 70)
    strategy_agent = create_strategy_planner()

    strategy = strategy_agent.create_strategy(
        product_info="Janus - AI GTM OS for technical founders",
        campaign_goal="Launch and acquire first 100 users",
        context={"timeline": "4 weeks", "budget": "low", "channels": ["X", "ProductHunt"]}
    )

    print(f"Campaign: {strategy['campaign_name']}")
    print(f"Goal: {strategy['campaign_goal']}")
    print(f"Phases: {len(strategy['phases'])}")
    for i, phase in enumerate(strategy['phases'], 1):
        print(f"  {i}. {phase['phase_name']} ({phase['duration']})")
    print(f"Campaign ID: {strategy['campaign_id']}")

    # 2. Content Creator
    print("\n✍️  Content Creator Agent")
    print("-" * 70)
    content_agent = create_content_creator()

    content = content_agent.create_content(
        request="Create a tweet announcing Janus launch",
        context={"brand_voice": "technical, friendly", "target_audience": "developers"}
    )

    print(f"Topic: {content['topic']}")
    print(f"\n[Variant A - {content['variants'][0]['hook']}]")
    print(f"{content['variants'][0]['content']}")
    print(f"Hashtags: {content['variants'][0]['hashtags']}")
    print(f"\n[Variant B - {content['variants'][1]['hook']}]")
    print(f"{content['variants'][1]['content']}")
    print(f"Hashtags: {content['variants'][1]['hashtags']}")
    print(f"\n💡 Recommendation: {content['recommendation']}")

    # 3. Metrics Analyzer
    print("\n📊 Metrics Analyzer Agent")
    print("-" * 70)
    metrics_agent = create_metrics_analyzer()

    # Analyze a tweet
    analysis = metrics_agent.analyze_tweet("tweet_001")
    print(f"Analyzing tweet_001...")
    print(f"Analysis output preview: {json.dumps(analysis, indent=2)}")


def demo_state_management():
    """Demo the state management system"""
    print_section("💾 STATE MANAGEMENT DEMO")

    # Create a campaign
    campaign = state.create_campaign(
        campaign_id="demo_campaign_001",
        name="Demo Product Launch",
        description="Demo campaign for Janus"
    )
    print(f"✅ Created campaign: {campaign.name}")
    print(f"   ID: {campaign.campaign_id}")
    print(f"   Phase: {campaign.phase.value}")

    # Update campaign strategy
    mermaid_diagram = """graph TD
    A[Start] --> B[Phase 1: Awareness]
    B --> C[Phase 2: Launch]
    C --> D[Phase 3: Growth]"""

    state.update_campaign_strategy("demo_campaign_001", mermaid_diagram)
    print(f"\n✅ Updated campaign strategy with Mermaid diagram")

    # Add insights
    state.add_campaign_insight("demo_campaign_001", "Engagement rate: 3.8% (above average)")
    state.add_campaign_insight("demo_campaign_001", "Best posting time: 2pm weekdays")
    print(f"\n✅ Added {len(campaign.insights)} insights to campaign")

    # Retrieve campaign
    retrieved = state.get_campaign("demo_campaign_001")
    print(f"\n📋 Campaign Details:")
    print(f"   Name: {retrieved.name}")
    print(f"   Phase: {retrieved.phase.value}")
    print(f"   Posts: {len(retrieved.posts)}")
    print(f"   Insights: {len(retrieved.insights)}")
    for i, insight in enumerate(retrieved.insights, 1):
        print(f"     {i}. {insight}")


def main():
    """Main demo function"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║         🚀 JANUS - AI-Powered GTM OS                             ║
    ║         Multi-Agent System Demo                                   ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables!")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Google API key to .env")
        print("3. Run the demo again")
        return

    print("✅ Google API Key found!")
    print("\nThis demo will showcase:")
    print("  1. Orchestrator coordinating all agents")
    print("  2. Individual agents working independently")
    print("  3. State management system")

    try:
        # Run demos
        # demo_orchestrator()
        demo_individual_agents()
        # demo_state_management()

        print_section("✅ DEMO COMPLETE")
        print("All agents are working correctly!")
        print("\nNext steps:")
        print("  - Check the README.md for detailed usage")
        print("  - Explore individual agent files for more examples")
        print("  - Integrate with your React frontend")
        print("  - Add real X API credentials for production")

    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
