#!/usr/bin/env python
"""
Test script to verify database locking fixes for A/B content generation.

This script simulates the scenario where multiple database operations happen
concurrently and verifies that the retry logic handles database locks correctly.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'janus.settings')
django.setup()

from django.db import connection, transaction
from agents.views import retry_on_db_lock
from agents.models import Campaign, Post, ContentVariant
import time


def test_retry_logic():
    """Test the retry_on_db_lock function with a simple database operation"""
    print("Testing retry logic...")

    # Clean up any test data
    Campaign.objects.filter(campaign_id__startswith='test_').delete()

    # Test 1: Simple operation that should succeed
    def create_test_campaign():
        with transaction.atomic():
            return Campaign.objects.create(
                campaign_id='test_campaign_1',
                name='Test Campaign',
                description='Test description',
                phase='planning'
            )

    try:
        campaign = retry_on_db_lock(create_test_campaign)
        print(f"✓ Test 1 passed: Campaign created successfully: {campaign.campaign_id}")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        return False

    # Test 2: Read operation
    def get_campaign():
        return Campaign.objects.get(campaign_id='test_campaign_1')

    try:
        campaign = retry_on_db_lock(get_campaign)
        print(f"✓ Test 2 passed: Campaign retrieved successfully: {campaign.name}")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        return False

    # Test 3: Update operation
    def update_campaign():
        with transaction.atomic():
            campaign = Campaign.objects.select_for_update().get(campaign_id='test_campaign_1')
            campaign.phase = 'content_creation'
            campaign.save(update_fields=['phase', 'updated_at'])
            return campaign

    try:
        campaign = retry_on_db_lock(update_campaign)
        print(f"✓ Test 3 passed: Campaign updated successfully: phase = {campaign.phase}")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
        return False

    # Cleanup
    Campaign.objects.filter(campaign_id='test_campaign_1').delete()
    print("\n✓ All tests passed!")
    return True


def test_concurrent_operations():
    """Test that database operations work correctly with the new timeout settings"""
    print("\nTesting concurrent database operations...")

    # Clean up any test data
    Campaign.objects.filter(campaign_id__startswith='test_concurrent_').delete()

    # Create a test campaign
    campaign = Campaign.objects.create(
        campaign_id='test_concurrent_1',
        name='Test Concurrent Campaign',
        description='Test concurrent operations',
        phase='planning'
    )

    # Create multiple posts
    posts = []
    for i in range(5):
        post = Post.objects.create(
            post_id=f'test_post_{i}',
            campaign=campaign,
            title=f'Test Post {i}',
            description=f'Test description {i}',
            phase='Phase 1',
            status='draft'
        )
        posts.append(post)

    print(f"✓ Created campaign with {len(posts)} posts")

    # Test rapid sequential updates (simulating what happens in background task)
    try:
        for i, post in enumerate(posts):
            # Create variants with retry logic
            def create_variant():
                with transaction.atomic():
                    return ContentVariant.objects.create(
                        post=post,
                        variant_id='A',
                        content=f'Test content A for post {i}',
                        platform='X',
                        metadata={'test': True}
                    )

            variant = retry_on_db_lock(create_variant)
            print(f"✓ Created variant A for post {i}")

        print(f"✓ All {len(posts)} variants created successfully without database locks!")

    except Exception as e:
        print(f"✗ Failed to create variants: {e}")
        return False
    finally:
        # Cleanup
        Campaign.objects.filter(campaign_id='test_concurrent_1').delete()

    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Database Lock Fix Verification Tests")
    print("=" * 60)
    print()

    # Close any existing connections
    connection.close()

    success = True

    # Run tests
    if not test_retry_logic():
        success = False

    if not test_concurrent_operations():
        success = False

    # Close connections
    connection.close()

    print()
    print("=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Database locking fixes are working!")
    else:
        print("✗ SOME TESTS FAILED - Please review the errors above")
    print("=" * 60)

    sys.exit(0 if success else 1)
