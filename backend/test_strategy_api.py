#!/usr/bin/env python
"""
Test script for Strategy Planning API

This script demonstrates how to use the Strategy Planning API endpoint.
Make sure the Django server is running before executing this script.

Usage:
    python test_strategy_api.py
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
STRATEGY_API_URL = f"{BASE_URL}/api/agents/strategy/"
CAMPAIGNS_API_URL = f"{BASE_URL}/api/agents/campaigns/"

def test_strategy_planning():
    """Test the strategy planning API endpoint"""

    print("=" * 80)
    print("Testing Strategy Planning API")
    print("=" * 80)

    # Request data
    request_data = {
        "product_description": (
            "Janus is an AI-powered GTM Operating System designed for technical founders. "
            "It automates marketing strategy planning, content creation with A/B testing, "
            "and metrics-driven optimization across social platforms like X and ProductHunt."
        ),
        "gtm_goals": "Launch product and acquire first 100 users in 4 weeks using X and ProductHunt",
        "campaign_name": "Janus Launch Campaign",
        "save_to_db": True
    }

    print("\n📤 Sending request to:", STRATEGY_API_URL)
    print("\nRequest payload:")
    print(json.dumps(request_data, indent=2))

    try:
        # Send POST request
        response = requests.post(
            STRATEGY_API_URL,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            print("\n✅ Success!")
            print(f"\nCampaign ID: {data.get('campaign_id')}")
            print(f"Total Posts: {data.get('total_posts')}")
            print(f"Message: {data.get('message')}")

            print(f"\nNodes: {len(data.get('nodes', []))} nodes created")
            print(f"Connections: {len(data.get('connections', []))} connections created")

            print("\n📊 Mermaid Diagram Preview (first 500 chars):")
            print("-" * 80)
            diagram = data.get('mermaid_diagram', '')
            print(diagram[:500] + "..." if len(diagram) > 500 else diagram)
            print("-" * 80)

            # Show sample nodes
            nodes = data.get('nodes', [])
            if nodes:
                print("\n📝 Sample Nodes:")
                for i, node in enumerate(nodes[:3]):
                    print(f"\n  {i+1}. {node['id']} - {node['phase']}")
                    print(f"     Title: {node['title']}")
                    print(f"     Description: {node['description'][:60]}...")

            return data
        else:
            print("\n❌ Error!")
            print(json.dumps(response.json(), indent=2))
            return None

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the Django server is running:")
        print("  cd src && python manage.py runserver")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def test_list_campaigns():
    """Test listing all campaigns"""

    print("\n" + "=" * 80)
    print("Testing Campaign List API")
    print("=" * 80)

    try:
        response = requests.get(CAMPAIGNS_API_URL)

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Found {data.get('count')} campaigns")

            campaigns = data.get('campaigns', [])
            if campaigns:
                print("\n📋 Recent Campaigns:")
                for i, campaign in enumerate(campaigns[:5]):
                    print(f"\n  {i+1}. {campaign['campaign_id']}")
                    print(f"     Name: {campaign['name']}")
                    print(f"     Phase: {campaign['phase']}")
                    print(f"     Posts: {campaign['posts_count']}")
                    print(f"     Created: {campaign['created_at']}")
        else:
            print("\n❌ Error!")
            print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_campaign_detail(campaign_id):
    """Test getting campaign details"""

    print("\n" + "=" * 80)
    print(f"Testing Campaign Detail API - {campaign_id}")
    print("=" * 80)

    url = f"{CAMPAIGNS_API_URL}{campaign_id}/"

    try:
        response = requests.get(url)

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            campaign = data.get('campaign', {})
            posts = data.get('posts', [])

            print(f"\n✅ Campaign Details:")
            print(f"  Name: {campaign['name']}")
            print(f"  Phase: {campaign['phase']}")
            print(f"  Total Posts: {len(posts)}")

            # Group posts by phase
            phase_groups = {}
            for post in posts:
                phase = post['phase']
                if phase not in phase_groups:
                    phase_groups[phase] = []
                phase_groups[phase].append(post)

            print(f"\n📊 Posts by Phase:")
            for phase in sorted(phase_groups.keys()):
                print(f"\n  {phase}: {len(phase_groups[phase])} posts")
                for post in phase_groups[phase][:3]:
                    print(f"    - {post['post_id']}: {post['title'][:50]}")

            return campaign
        else:
            print("\n❌ Error!")
            print(json.dumps(response.json(), indent=2))
            return None

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def monitor_campaign_phase_transitions(campaign_id, max_wait=120, check_interval=5):
    """
    Monitor campaign phase transitions to verify background content generation.

    Expected flow:
    1. planning → content_creation (when background task starts)
    2. content_creation → scheduled (when content generation completes)

    Args:
        campaign_id: ID of campaign to monitor
        max_wait: Maximum time to wait in seconds (default: 120)
        check_interval: How often to check in seconds (default: 5)
    """
    print("\n" + "=" * 80)
    print("Monitoring Campaign Phase Transitions")
    print("=" * 80)

    print(f"\nCampaign ID: {campaign_id}")
    print(f"Monitoring for up to {max_wait} seconds...")
    print(f"Checking every {check_interval} seconds...\n")

    url = f"{CAMPAIGNS_API_URL}{campaign_id}/"
    phases_seen = []
    variants_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < max_wait:
            # Get campaign details
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                campaign = data.get('campaign', {})
                posts = data.get('posts', [])

                current_phase = campaign['phase']

                # Track phase changes
                if not phases_seen or current_phase != phases_seen[-1]:
                    if phases_seen:
                        print(f"✓ Phase transition: {phases_seen[-1]} → {current_phase}")
                    else:
                        print(f"Initial phase: {current_phase}")
                    phases_seen.append(current_phase)

                # Count variants across all posts
                new_variants_count = 0
                for post in posts:
                    new_variants_count += len(post.get('variants', []))

                # Track variant generation
                if new_variants_count > variants_count:
                    print(f"✓ Variants generated: {variants_count} → {new_variants_count}")
                    variants_count = new_variants_count

                # Check if we reached scheduled phase
                if current_phase == 'scheduled':
                    print(f"\n✅ Campaign reached 'scheduled' phase!")
                    break

                time.sleep(check_interval)
            else:
                print(f"⚠️  Error fetching campaign: {response.status_code}")
                break

        # Final summary
        print("\n" + "="*80)
        print("MONITORING SUMMARY")
        print("="*80)
        print(f"Phase transitions: {' → '.join(phases_seen)}")
        print(f"Total variants generated: {variants_count}")

        # Verify expected behavior
        expected_phases = ['planning', 'content_creation', 'scheduled']

        print("\n✅ Verification:")
        if 'content_creation' in phases_seen:
            print("  ✓ Campaign entered 'content_creation' phase")
        else:
            print("  ⚠️  Campaign did not enter 'content_creation' phase")

        if 'scheduled' in phases_seen:
            print("  ✓ Campaign reached 'scheduled' phase")
        else:
            print("  ⚠️  Campaign has not reached 'scheduled' phase yet")

        if variants_count > 0:
            print(f"  ✓ Content variants were generated ({variants_count} total)")
        else:
            print("  ⚠️  No content variants generated yet")

        return phases_seen

    except Exception as e:
        print(f"\n❌ Error during monitoring: {str(e)}")
        return phases_seen


def main():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         🚀 JANUS - Strategy Planning API Test                             ║
║         With Automatic Background Content Generation                      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Create a strategy
    result = test_strategy_planning()

    # Test 2: Monitor phase transitions (NEW - tests automatic content generation)
    if result and result.get('campaign_id'):
        campaign_id = result['campaign_id']

        print("\n" + "=" * 80)
        print("ℹ️  Background content generation has been triggered automatically!")
        print("   The campaign will transition through the following phases:")
        print("   1. planning → content_creation")
        print("   2. content_creation → scheduled")
        print("=" * 80)

        # Wait a moment for background task to start
        time.sleep(2)

        # Monitor campaign phase transitions
        monitor_campaign_phase_transitions(campaign_id, max_wait=180, check_interval=5)

    # Test 3: List campaigns
    test_list_campaigns()

    # Test 4: Get campaign detail (if we created one)
    if result and result.get('campaign_id'):
        test_campaign_detail(result['campaign_id'])

    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
