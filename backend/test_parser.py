#!/usr/bin/env python3
"""
Comprehensive Test Suite for Mermaid Parser

Tests the mermaid parser with various edge cases and scenarios:
1. Valid diagram with 3 phases, multiple nodes, connections
2. Diagram with missing <title> or <description> tags (should skip gracefully)
3. Diagram with malformed nodes
4. Empty diagram
5. Diagram with only 1 phase
"""

import json
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.mermaid_parser import parse_mermaid_diagram


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def print_test_header(test_number: int, test_name: str) -> None:
    """Print a formatted test header."""
    print(f"\n{'─' * 80}")
    print(f"TEST {test_number}: {test_name}")
    print(f"{'─' * 80}\n")


def print_input(mermaid_string: str) -> None:
    """Print the input mermaid string."""
    print("INPUT MERMAID DIAGRAM:")
    print("─" * 40)
    print(mermaid_string)
    print("─" * 40 + "\n")


def print_output(result: dict) -> None:
    """Print the parsed output in a readable format."""
    print("OUTPUT:")
    print("─" * 40)
    print(json.dumps(result, indent=2))
    print("─" * 40 + "\n")


def print_analysis(result: dict) -> None:
    """Print analysis of the result."""
    print("ANALYSIS:")
    print(f"  • Total Nodes: {len(result['nodes'])}")
    print(f"  • Total Connections: {len(result['connections'])}")

    # Count phases
    phases = set(node.get('phase', 'Unknown') for node in result['nodes'])
    print(f"  • Unique Phases: {len(phases)}")
    if phases:
        print(f"  • Phase Names: {', '.join(sorted(phases))}")
    print()


def verify_expected(result: dict, expected: dict, test_name: str) -> bool:
    """Verify if the result matches expected values."""
    print("VERIFICATION:")

    node_count_match = len(result['nodes']) == expected.get('node_count', 0)
    conn_count_match = len(result['connections']) == expected.get('connection_count', 0)

    print(f"  ✓ Node count: {len(result['nodes'])} (expected: {expected.get('node_count', 0)}) - {'PASS' if node_count_match else 'FAIL'}")
    print(f"  ✓ Connection count: {len(result['connections'])} (expected: {expected.get('connection_count', 0)}) - {'PASS' if conn_count_match else 'FAIL'}")

    if 'phase_count' in expected:
        phases = set(node.get('phase', 'Unknown') for node in result['nodes'])
        phase_count_match = len(phases) == expected['phase_count']
        print(f"  ✓ Phase count: {len(phases)} (expected: {expected['phase_count']}) - {'PASS' if phase_count_match else 'FAIL'}")
    else:
        phase_count_match = True

    if 'should_be_empty' in expected:
        is_empty = len(result['nodes']) == 0 and len(result['connections']) == 0
        print(f"  ✓ Should be empty: {is_empty} (expected: {expected['should_be_empty']}) - {'PASS' if is_empty == expected['should_be_empty'] else 'FAIL'}")
        empty_match = is_empty == expected['should_be_empty']
    else:
        empty_match = True

    all_pass = node_count_match and conn_count_match and phase_count_match and empty_match

    print(f"\n  {'✅ TEST PASSED' if all_pass else '❌ TEST FAILED'}\n")
    return all_pass


# ============================================================================
# TEST CASE 1: Valid Diagram with 3 Phases, Multiple Nodes, Connections
# ============================================================================

def test_1_valid_multi_phase_diagram():
    """Test a valid diagram with 3 phases, multiple nodes, and connections."""
    print_test_header(1, "Valid Diagram with 3 Phases, Multiple Nodes, Connections")

    mermaid_string = """
graph TB
    subgraph "Phase 1: Awareness"
        NODE1[<title>X Platform Posts</title><description>Build anticipation with teaser posts</description>]
        NODE2[<title>ProductHunt Teaser</title><description>Create coming soon page</description>]
        NODE3[<title>Community Engagement</title><description>Engage with tech communities</description>]
    end
    subgraph "Phase 2: Launch"
        NODE4[<title>ProductHunt Launch</title><description>Official launch on ProductHunt</description>]
        NODE5[<title>X Announcement Thread</title><description>Detailed announcement thread</description>]
        NODE6[<title>Demo Video</title><description>Product walkthrough video</description>]
    end
    subgraph "Phase 3: Growth"
        NODE7[<title>Content Marketing</title><description>Weekly blog posts and tutorials</description>]
        NODE8[<title>A/B Testing</title><description>Test different messaging variants</description>]
        NODE9[<title>Metrics Analysis</title><description>Analyze and optimize based on metrics</description>]
    end
    NODE1 --> NODE2
    NODE2 --> NODE3
    NODE3 --> NODE4
    NODE4 --> NODE5
    NODE5 --> NODE6
    NODE6 --> NODE7
    NODE7 --> NODE8
    NODE8 --> NODE9
"""

    print_input(mermaid_string)

    result = parse_mermaid_diagram(mermaid_string)

    print_output(result)
    print_analysis(result)

    expected = {
        'node_count': 9,
        'connection_count': 8,
        'phase_count': 3
    }

    return verify_expected(result, expected, "Valid Multi-Phase Diagram")


# ============================================================================
# TEST CASE 2: Diagram with Missing <title> or <description> Tags
# ============================================================================

def test_2_missing_tags():
    """Test diagram with missing title or description tags - should skip gracefully."""
    print_test_header(2, "Diagram with Missing <title> or <description> Tags")

    mermaid_string = """
graph TB
    subgraph "Phase 1"
        NODE1[<title>Valid Node</title><description>This one has both tags</description>]
        NODE2[<title>Missing Description</title>]
        NODE3[<description>Missing Title</description>]
        NODE4[No tags at all just text]
        NODE5[<title>Another Valid</title><description>This should work</description>]
    end
    NODE1 --> NODE5
"""

    print_input(mermaid_string)

    result = parse_mermaid_diagram(mermaid_string)

    print_output(result)
    print_analysis(result)

    print("EXPECTED BEHAVIOR:")
    print("  • Only nodes with BOTH <title> and <description> tags should be parsed")
    print("  • Invalid nodes should be skipped silently")
    print("  • NODE1 and NODE5 should be parsed successfully")
    print("  • NODE2, NODE3, NODE4 should be skipped\n")

    expected = {
        'node_count': 2,  # Only NODE1 and NODE5
        'connection_count': 1,
        'phase_count': 1
    }

    return verify_expected(result, expected, "Missing Tags")


# ============================================================================
# TEST CASE 3: Diagram with Malformed Nodes
# ============================================================================

def test_3_malformed_nodes():
    """Test diagram with various malformed node definitions."""
    print_test_header(3, "Diagram with Malformed Nodes")

    mermaid_string = """
graph TB
    subgraph "Phase 1"
        NODE1[<title>Valid Node</title><description>Properly formatted</description>]
        NODE2[<title>Unclosed Tag<description>Missing closing title tag</description>]
        NODE3<title>Wrong Brackets</title><description>Using angle brackets</description>
        [<title>No ID</title><description>Missing node ID</description>]
        NODE5[]
        NODE6[<title></title><description></description>]
        NODE7[<title>Valid Again</title><description>This should parse</description>]
    end
    NODE1 --> NODE7
    NODE1 --> NONEXISTENT
"""

    print_input(mermaid_string)

    result = parse_mermaid_diagram(mermaid_string)

    print_output(result)
    print_analysis(result)

    print("EXPECTED BEHAVIOR:")
    print("  • Parser should gracefully skip malformed nodes")
    print("  • Only properly formatted nodes (NODE1, NODE7) should be parsed")
    print("  • Connections to non-existent nodes should still be recorded")
    print("  • Empty title/description tags (NODE6) should be parsed but with empty strings\n")

    expected = {
        'node_count': 3,  # NODE1, NODE6 (empty strings), NODE7
        'connection_count': 2,
        'phase_count': 1
    }

    return verify_expected(result, expected, "Malformed Nodes")


# ============================================================================
# TEST CASE 4: Empty Diagram
# ============================================================================

def test_4_empty_diagram():
    """Test empty or nearly empty diagrams."""
    print_test_header(4, "Empty Diagram")

    test_cases = [
        ("Empty string", ""),
        ("Only whitespace", "   \n\n   \t\n  "),
        ("Only graph declaration", "graph TB"),
        ("Graph with empty subgraph", """
graph TB
    subgraph "Empty Phase"
    end
"""),
    ]

    all_passed = True

    for idx, (name, mermaid_string) in enumerate(test_cases, 1):
        print(f"\nSub-test 4.{idx}: {name}")
        print("─" * 40)
        print(f"Input: {repr(mermaid_string)}")

        result = parse_mermaid_diagram(mermaid_string)

        print_output(result)

        expected = {
            'node_count': 0,
            'connection_count': 0,
            'should_be_empty': True
        }

        passed = verify_expected(result, expected, f"Empty Diagram - {name}")
        all_passed = all_passed and passed

    return all_passed


# ============================================================================
# TEST CASE 5: Diagram with Only 1 Phase
# ============================================================================

def test_5_single_phase():
    """Test diagram with only one phase."""
    print_test_header(5, "Diagram with Only 1 Phase")

    mermaid_string = """
graph TB
    subgraph "Launch Phase"
        NODE1[<title>ProductHunt Launch</title><description>Launch on ProductHunt</description>]
        NODE2[<title>Social Media Announcement</title><description>Announce on X and LinkedIn</description>]
        NODE3[<title>Email Campaign</title><description>Send to email list</description>]
        NODE4[<title>Monitor Metrics</title><description>Track launch metrics</description>]
    end
    NODE1 --> NODE2
    NODE2 --> NODE3
    NODE3 --> NODE4
"""

    print_input(mermaid_string)

    result = parse_mermaid_diagram(mermaid_string)

    print_output(result)
    print_analysis(result)

    print("EXPECTED BEHAVIOR:")
    print("  • All nodes should be in the same phase")
    print("  • Phase name should be 'Launch Phase'")
    print("  • All connections should be preserved\n")

    expected = {
        'node_count': 4,
        'connection_count': 3,
        'phase_count': 1
    }

    return verify_expected(result, expected, "Single Phase")


# ============================================================================
# BONUS TEST: Complex Real-World Scenario
# ============================================================================

def test_bonus_complex_scenario():
    """Test a complex real-world scenario mixing various cases."""
    print_test_header("BONUS", "Complex Real-World Scenario")

    mermaid_string = """
graph TB
    subgraph "Pre-Launch"
        PRE1[<title>Market Research</title><description>Analyze target market</description>]
        PRE2[<title>Strategy Planning</title><description>Create go-to-market strategy</description>]
    end

    subgraph "Launch"
        LAUNCH1[<title>ProductHunt Launch</title><description>Official PH launch</description>]
        LAUNCH2[Invalid node format here]
        LAUNCH3[<title>PR Outreach</title><description>Reach out to tech publications</description>]
    end

    subgraph "Post-Launch"
        POST1[<title>Metrics Analysis</title><description>Analyze launch metrics</description>]
        POST2[<title>Iteration</title><description>Iterate based on feedback</description>]
    end

    PRE1 --> PRE2
    PRE2 --> LAUNCH1
    LAUNCH1 --> LAUNCH3
    LAUNCH3 --> POST1
    POST1 --> POST2
    POST2 --> PRE1
"""

    print_input(mermaid_string)

    result = parse_mermaid_diagram(mermaid_string)

    print_output(result)
    print_analysis(result)

    print("EXPECTED BEHAVIOR:")
    print("  • Should handle multiple phases correctly")
    print("  • Should skip invalid node (LAUNCH2)")
    print("  • Should preserve all valid connections")
    print("  • Should handle circular connection (POST2 --> PRE1)\n")

    expected = {
        'node_count': 6,  # All except LAUNCH2
        'connection_count': 6,
        'phase_count': 3
    }

    return verify_expected(result, expected, "Complex Scenario")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and report results."""
    print_section_header("MERMAID PARSER TEST SUITE")

    print("This test suite validates the mermaid parser's ability to:")
    print("  1. Parse valid multi-phase diagrams")
    print("  2. Handle missing tags gracefully")
    print("  3. Skip malformed nodes")
    print("  4. Handle empty diagrams")
    print("  5. Process single-phase diagrams")
    print("  BONUS: Handle complex real-world scenarios")

    # Run all tests
    results = {
        "Test 1 - Valid Multi-Phase": test_1_valid_multi_phase_diagram(),
        "Test 2 - Missing Tags": test_2_missing_tags(),
        "Test 3 - Malformed Nodes": test_3_malformed_nodes(),
        "Test 4 - Empty Diagram": test_4_empty_diagram(),
        "Test 5 - Single Phase": test_5_single_phase(),
        "Bonus - Complex Scenario": test_bonus_complex_scenario(),
    }

    # Print summary
    print_section_header("TEST SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")

    print(f"\n{'=' * 80}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'=' * 80}\n")

    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
