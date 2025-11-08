#!/usr/bin/env python
"""
Janus Multi-Agent System Demo - 3 Scenario Workflow

Demonstrates the complete workflow of the Janus GTM OS:
- Scenario 1: Strategy Planning → Mermaid Diagram → Save to DB
- Scenario 2: Generate A/B Content for all nodes
- Scenario 3: Metrics Analysis → Improved Content

Make sure to set GOOGLE_API_KEY in your .env file before running.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "janus.settings")
import django
django.setup()

from agents.strategy_planner import create_strategy_planner
from agents.content_creator import create_content_creator
from agents.metrics_analyzer import create_metrics_analyzer
from agents.mermaid_parser import parse_mermaid_diagram
from agents.models import Campaign, Post, ContentVariant


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80 + "\n")


def load_placeholder_metrics() -> Dict:
    """Load placeholder metrics from JSON file"""
    metrics_file = Path(__file__).parent / "src" / "agents" / "data" / "placeholder_metrics.json"
    with open(metrics_file, 'r') as f:
        return json.load(f)


def scenario_1_strategy_planning(product_description: str, gtm_goals: str) -> tuple[str, Campaign]:
    """
    Scenario 1: Strategy Planning

    Flow:
    1. User provides product description and GTM goals
    2. Strategy Planner creates mermaid diagram with 3 phases
    3. Parse mermaid diagram
    4. Save to database (Campaign + Posts with connections)
    5. Return diagram to user

    Returns:
        tuple: (mermaid_diagram, campaign_object)
    """
    print_section("📋 SCENARIO 1: STRATEGY PLANNING")

    # Step 1: Create strategy with Strategy Planner
    print("Step 1: Generating GTM strategy with 3 phases...")
    strategy_agent = create_strategy_planner()
    strategy_output = strategy_agent.execute(product_description, gtm_goals)
    mermaid_diagram = strategy_output.diagram

    print("✅ Strategy created!")
    print("\nMermaid Diagram:")
    print("-" * 80)
    print(mermaid_diagram)
    print("-" * 80)

    # Step 2: Parse mermaid diagram
    print("\nStep 2: Parsing mermaid diagram...")
    parsed_data = parse_mermaid_diagram(mermaid_diagram)

    print(f"✅ Parsed {len(parsed_data['nodes'])} nodes and {len(parsed_data['connections'])} connections")
    print(f"\nNodes by phase:")
    phase_counts = {}
    for node in parsed_data['nodes']:
        phase = node['phase']
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
    for phase, count in sorted(phase_counts.items()):
        print(f"  - {phase}: {count} nodes")

    # Step 3: Save to database
    print("\nStep 3: Saving to database...")

    # Create campaign
    campaign = Campaign.objects.create(
        campaign_id=f"campaign_{Campaign.objects.count() + 1}",
        name="GTM Campaign",
        description=product_description,
        strategy=mermaid_diagram,
        phase="strategizing"
    )
    print(f"✅ Created Campaign: {campaign.campaign_id}")

    # Create posts from nodes
    node_to_post = {}  # Map node IDs to Post objects for later linking

    for node in parsed_data['nodes']:
        post = Post.objects.create(
            post_id=f"post_{node['id']}",
            campaign=campaign,
            title=node['title'],
            description=node['description'],
            phase=node['phase'] if node['phase'] in ['Phase 1', 'Phase 2', 'Phase 3'] else 'Phase 1',
            status='draft'
        )
        node_to_post[node['id']] = post
        print(f"  Created Post: {node['id']} - {node['title'][:50]}...")

    # Link posts using next_posts based on connections
    print(f"\nStep 4: Linking posts based on {len(parsed_data['connections'])} connections...")
    for connection in parsed_data['connections']:
        from_node = connection['from']
        to_node = connection['to']

        if from_node in node_to_post and to_node in node_to_post:
            from_post = node_to_post[from_node]
            to_post = node_to_post[to_node]
            from_post.next_posts.add(to_post)
            print(f"  Linked: {from_node} → {to_node}")

    print(f"\n✅ Scenario 1 Complete!")
    print(f"   Campaign ID: {campaign.campaign_id}")
    print(f"   Total Posts: {campaign.posts.count()}")
    print(f"   Strategy saved to database")

    return mermaid_diagram, campaign


def scenario_2_generate_ab_content(campaign: Campaign, product_info: str):
    """
    Scenario 2: Generate A/B Content for ALL nodes

    Flow:
    1. Get all posts from campaign
    2. For each post, generate A/B content using Content Creator
    3. Save ContentVariant A and B for each post

    Args:
        campaign: Campaign object from Scenario 1
        product_info: Product description for content generation
    """
    print_section("✍️  SCENARIO 2: GENERATE A/B CONTENT FOR ALL NODES")

    content_agent = create_content_creator()
    posts = campaign.posts.all().order_by('phase', 'post_id')

    print(f"Generating A/B content for {posts.count()} posts...")

    for i, post in enumerate(posts, 1):
        print(f"\nPost {i}/{posts.count()}: {post.title}")
        print(f"Phase: {post.phase} | Description: {post.description[:60]}...")

        # Generate A/B content
        content_output = content_agent.execute(
            title=post.title,
            description=post.description,
            product_info=product_info
        )

        # Create ContentVariant A
        variant_a = ContentVariant.objects.create(
            post=post,
            variant_label='A',
            content=content_output.A,
            platform='X',
            status='draft'
        )

        # Create ContentVariant B
        variant_b = ContentVariant.objects.create(
            post=post,
            variant_label='B',
            content=content_output.B,
            platform='X',
            status='draft'
        )

        print(f"  ✅ Variant A ({len(content_output.A)} chars): {content_output.A[:60]}...")
        print(f"  ✅ Variant B ({len(content_output.B)} chars): {content_output.B[:60]}...")

    print(f"\n✅ Scenario 2 Complete!")
    print(f"   Generated {posts.count() * 2} content variants (A/B for each post)")


def scenario_3_metrics_analysis_and_improvement(campaign: Campaign, product_info: str):
    """
    Scenario 3: Metrics Analysis → Improved Content

    Flow:
    1. Load placeholder metrics from JSON
    2. Pass to Metrics Analyzer
    3. Get analyzed_report
    4. Pass report + old content to Content Creator
    5. Generate improved A/B variants
    6. Save new variants

    Args:
        campaign: Campaign object
        product_info: Product description
    """
    print_section("📊 SCENARIO 3: METRICS ANALYSIS & CONTENT IMPROVEMENT")

    # Step 1: Load placeholder metrics
    print("Step 1: Loading placeholder metrics...")
    metrics_data = load_placeholder_metrics()
    print(f"✅ Loaded metrics for {len(metrics_data['data'])} tweets")

    # Display sample metrics
    sample_tweet = metrics_data['data'][0]
    print(f"\nSample Tweet Metrics:")
    print(f"  Text: {sample_tweet['text'][:60]}...")
    print(f"  Impressions: {sample_tweet['public_metrics']['impression_count']:,}")
    print(f"  Likes: {sample_tweet['public_metrics']['like_count']}")
    print(f"  Engagement Rate: {sample_tweet['engagement_rate']:.2f}%")

    # Step 2: Analyze metrics
    print("\nStep 2: Analyzing metrics with Metrics Analyzer...")
    metrics_agent = create_metrics_analyzer()
    analysis = metrics_agent.execute(metrics_data)

    print("✅ Metrics analyzed!")
    print("\nAnalyzed Report (first 500 chars):")
    print("-" * 80)
    print(analysis.analyzed_report[:500] + "...")
    print("-" * 80)

    # Step 3: Generate improved content for first 3 posts
    print("\nStep 3: Generating improved A/B content based on metrics...")
    content_agent = create_content_creator()

    posts = campaign.posts.all()[:3]  # Improve first 3 posts as example

    for i, post in enumerate(posts, 1):
        # Get old content (from existing variants)
        old_variants = post.variants.all()
        if not old_variants.exists():
            print(f"  ⚠️  Post {i}: No existing content to improve, skipping...")
            continue

        old_content_a = old_variants.filter(variant_label='A').first()
        old_content = old_content_a.content if old_content_a else ""

        print(f"\nPost {i}: {post.title}")
        print(f"  Old content: {old_content[:60]}...")

        # Generate improved content
        improved_output = content_agent.execute_with_metrics(
            title=post.title,
            description=post.description,
            product_info=product_info,
            old_content=old_content,
            analyzed_report=analysis.analyzed_report
        )

        # Update existing variants or create new ones
        variant_a = old_variants.filter(variant_label='A').first()
        variant_b = old_variants.filter(variant_label='B').first()

        if variant_a:
            variant_a.content = improved_output.A
            variant_a.save()
        else:
            variant_a = ContentVariant.objects.create(
                post=post,
                variant_label='A',
                content=improved_output.A,
                platform='X',
                status='draft'
            )

        if variant_b:
            variant_b.content = improved_output.B
            variant_b.save()
        else:
            variant_b = ContentVariant.objects.create(
                post=post,
                variant_label='B',
                content=improved_output.B,
                platform='X',
                status='draft'
            )

        print(f"  ✅ Improved Variant A: {improved_output.A[:60]}...")
        print(f"  ✅ Improved Variant B: {improved_output.B[:60]}...")

    print(f"\n✅ Scenario 3 Complete!")
    print(f"   Improved {posts.count()} posts based on metrics analysis")


def run_sequential_demo():
    """Run all 3 scenarios in sequence"""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║         🚀 JANUS - AI-Powered GTM OS                                      ║
    ║         Sequential Workflow Demo (Scenario 1 → 2 → 3)                     ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Define product info
    product_description = (
        "Janus is an AI-powered GTM Operating System designed for technical founders. "
        "It automates marketing strategy planning, content creation with A/B testing, "
        "and metrics-driven optimization across social platforms like X and ProductHunt."
    )
    gtm_goals = "Launch product and acquire first 100 users in 4 weeks using X and ProductHunt"

    print("Product:", product_description[:80] + "...")
    print("Goal:", gtm_goals)

    try:
        # Scenario 1: Strategy Planning
        mermaid_diagram, campaign = scenario_1_strategy_planning(product_description, gtm_goals)

        input("\n⏸️  Press Enter to continue to Scenario 2...")

        # Scenario 2: Generate A/B Content
        scenario_2_generate_ab_content(campaign, product_description)

        input("\n⏸️  Press Enter to continue to Scenario 3...")

        # Scenario 3: Metrics Analysis & Improvement
        scenario_3_metrics_analysis_and_improvement(campaign, product_description)

        print_section("✅ SEQUENTIAL DEMO COMPLETE")
        print("All 3 scenarios executed successfully!")
        print(f"\nFinal Campaign Stats:")
        print(f"  Campaign ID: {campaign.campaign_id}")
        print(f"  Total Posts: {campaign.posts.count()}")
        print(f"  Total Variants: {ContentVariant.objects.filter(post__campaign=campaign).count()}")

    except Exception as e:
        print(f"\n❌ Error during sequential demo: {str(e)}")
        import traceback
        traceback.print_exc()


def run_independent_demos():
    """Run each scenario independently with hardcoded data"""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║         🚀 JANUS - AI-Powered GTM OS                                      ║
    ║         Independent Scenario Demos                                         ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)

    product_description = (
        "Janus is an AI-powered GTM Operating System for technical founders. "
        "Automates marketing strategy, content creation, and optimization."
    )
    gtm_goals = "Launch and get 100 users in 4 weeks via X and ProductHunt"

    try:
        # Independent Scenario 1
        print("\n🔹 Running Scenario 1 independently...")
        _, campaign1 = scenario_1_strategy_planning(product_description, gtm_goals)

        # Independent Scenario 2 (create new campaign)
        print("\n🔹 Running Scenario 2 independently...")
        _, campaign2 = scenario_1_strategy_planning(product_description, gtm_goals)
        scenario_2_generate_ab_content(campaign2, product_description)

        # Independent Scenario 3 (create new campaign with content)
        print("\n🔹 Running Scenario 3 independently...")
        _, campaign3 = scenario_1_strategy_planning(product_description, gtm_goals)
        scenario_2_generate_ab_content(campaign3, product_description)
        scenario_3_metrics_analysis_and_improvement(campaign3, product_description)

        print_section("✅ INDEPENDENT DEMOS COMPLETE")
        print("All scenarios ran independently!")

    except Exception as e:
        print(f"\n❌ Error during independent demos: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function"""
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables!")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Google API key to .env")
        print("3. Run the demo again")
        return

    print("✅ Google API Key found!")

    # Choose demo mode
    print("\nSelect demo mode:")
    print("  1. Sequential (Scenario 1 → 2 → 3)")
    print("  2. Independent (Each scenario separately)")
    print("  3. Both")

    choice = input("\nEnter choice (1/2/3) [default: 1]: ").strip() or "1"

    if choice == "1":
        run_sequential_demo()
    elif choice == "2":
        run_independent_demos()
    elif choice == "3":
        run_sequential_demo()
        input("\n⏸️  Press Enter to run independent demos...")
        run_independent_demos()
    else:
        print("Invalid choice. Running sequential demo by default.")
        run_sequential_demo()

    print("\n" + "=" * 80)
    print("Next steps:")
    print("  - Check Django admin to view saved campaigns and posts")
    print("  - Integrate with React frontend")
    print("  - Add real X API credentials for production")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
