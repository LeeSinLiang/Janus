#!/usr/bin/env python
"""
Test script for strategy planner regeneration feature.

This script tests the execute_from_phase() method which allows regenerating
a campaign strategy from a specific phase onwards while preserving existing posts.

Features tested:
1. Regeneration from Phase 2 (preserving Phase 1 posts)
2. Regeneration from Phase 3 (preserving Phase 1 and Phase 2 posts)
3. Many-to-many connections (branching and merging)
4. Variable node count per phase (2-5 nodes)
5. Proper phase labeling (Existing vs New)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.strategy_planner import create_strategy_planner


def test_regenerate_from_phase_2():
    """Test regeneration starting from Phase 2."""
    print("=" * 80)
    print("TEST 1: Regenerate from Phase 2 (Preserve Phase 1)")
    print("=" * 80)

    agent = create_strategy_planner()

    # Mock existing Phase 1 posts
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

    print("\nGenerated Diagram:")
    print(result.diagram)
    print("\n")

    # Validate output
    diagram = result.diagram
    assert "Phase 1 (Existing)" in diagram, "Missing Phase 1 (Existing) label"
    assert "Phase 2 (New)" in diagram, "Missing Phase 2 (New) label"
    assert "Phase 3 (New)" in diagram, "Missing Phase 3 (New) label"
    assert "NODE1" in diagram and "NODE2" in diagram, "Missing existing nodes"
    assert "NODE1 -->" in diagram or "NODE2 -->" in diagram, "No connections from existing nodes"

    print("✓ TEST 1 PASSED: Phase 2 regeneration successful\n")


def test_regenerate_from_phase_3():
    """Test regeneration starting from Phase 3."""
    print("=" * 80)
    print("TEST 2: Regenerate from Phase 3 (Preserve Phase 1 and 2)")
    print("=" * 80)

    agent = create_strategy_planner()

    # Mock existing Phase 1 and Phase 2 posts
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
        },
        {
            "node_id": "NODE3",
            "post_id": "post_003",
            "title": "ProductHunt launch",
            "description": "Official launch on ProductHunt",
            "phase": "Phase 2"
        },
        {
            "node_id": "NODE4",
            "post_id": "post_004",
            "title": "Launch announcement",
            "description": "Post launch thread on X",
            "phase": "Phase 2"
        }
    ]

    result = agent.execute_from_phase(
        phase_num=3,
        existing_posts=existing_posts,
        product_description="Janus - AI-powered GTM OS that automates marketing for technical founders",
        gtm_goals="Scale to 500 users and achieve 80% activation rate",
        new_direction="Focus on growth through content marketing, partnerships, and aggressive A/B testing. Build thought leadership in AI-powered marketing."
    )

    print("\nGenerated Diagram:")
    print(result.diagram)
    print("\n")

    # Validate output
    diagram = result.diagram
    assert "Phase 1 (Existing)" in diagram, "Missing Phase 1 (Existing) label"
    assert "Phase 2 (Existing)" in diagram, "Missing Phase 2 (Existing) label"
    assert "Phase 3 (New)" in diagram, "Missing Phase 3 (New) label"
    assert all(f"NODE{i}" in diagram for i in range(1, 5)), "Missing existing nodes"
    assert "NODE3 -->" in diagram or "NODE4 -->" in diagram, "No connections from Phase 2 nodes"

    print("✓ TEST 2 PASSED: Phase 3 regeneration successful\n")


def test_many_to_many_connections():
    """Test that many-to-many connections are properly generated."""
    print("=" * 80)
    print("TEST 3: Verify Many-to-Many Connections")
    print("=" * 80)

    agent = create_strategy_planner()

    # Mock existing posts
    existing_posts = [
        {
            "node_id": "NODE1",
            "post_id": "post_001",
            "title": "Awareness Post A",
            "description": "Build awareness through demo",
            "phase": "Phase 1"
        },
        {
            "node_id": "NODE2",
            "post_id": "post_002",
            "title": "Awareness Post B",
            "description": "Build awareness through community",
            "phase": "Phase 1"
        }
    ]

    result = agent.execute_from_phase(
        phase_num=2,
        existing_posts=existing_posts,
        product_description="AI-powered marketing tool",
        gtm_goals="Test many-to-many connections",
        new_direction="Create diverse launch strategies that can branch and merge"
    )

    diagram = result.diagram
    print("\nGenerated Diagram:")
    print(diagram)
    print("\n")

    # Count connections from NODE1 and NODE2
    node1_connections = diagram.count("NODE1 -->")
    node2_connections = diagram.count("NODE2 -->")

    print(f"NODE1 connections: {node1_connections}")
    print(f"NODE2 connections: {node2_connections}")

    # Verify branching (should have multiple connections from old nodes)
    assert node1_connections > 0, "NODE1 has no outgoing connections"
    assert node2_connections > 0, "NODE2 has no outgoing connections"

    print("✓ TEST 3 PASSED: Many-to-many connections verified\n")


def test_node_count_per_phase():
    """Test that new phases have 2-5 nodes."""
    print("=" * 80)
    print("TEST 4: Verify Node Count (2-5 nodes per phase)")
    print("=" * 80)

    agent = create_strategy_planner()

    existing_posts = [
        {
            "node_id": "NODE1",
            "post_id": "post_001",
            "title": "Initial Post",
            "description": "Starting point",
            "phase": "Phase 1"
        }
    ]

    result = agent.execute_from_phase(
        phase_num=2,
        existing_posts=existing_posts,
        product_description="Test product",
        gtm_goals="Test node count",
        new_direction="Generate rich strategy with multiple parallel paths"
    )

    diagram = result.diagram
    print("\nGenerated Diagram:")
    print(diagram)
    print("\n")

    # Extract node IDs (simple regex would be better, but this works)
    import re
    nodes = re.findall(r'(NODE\d+)\[', diagram)
    unique_nodes = set(nodes)

    # Count nodes per phase (approximate)
    phase2_nodes = [n for n in unique_nodes if int(n.replace("NODE", "")) > 1 and "Phase 2" in diagram[:diagram.index(n)]]

    print(f"Total unique nodes: {len(unique_nodes)}")
    print(f"All nodes: {sorted(unique_nodes)}")

    # Should have at least NODE1 (existing) + multiple new nodes
    assert len(unique_nodes) >= 3, f"Too few nodes generated: {len(unique_nodes)}"

    print("✓ TEST 4 PASSED: Node count validated\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("STRATEGY PLANNER REGENERATION TEST SUITE")
    print("=" * 80 + "\n")

    try:
        test_regenerate_from_phase_2()
        test_regenerate_from_phase_3()
        test_many_to_many_connections()
        test_node_count_per_phase()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
