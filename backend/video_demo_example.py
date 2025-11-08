#!/usr/bin/env python
"""
Example: How to use create_video() and save to Django ContentVariant asset field

This shows the pattern for saving generated videos to the database.
"""

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

from agents.media_creator import create_media_creator
from agents.models import Campaign, Post, ContentVariant
from django.core.files import File


def example_video_generation():
    """Example of generating a video and saving to ContentVariant"""

    # Step 1: Create media agent for video
    print("Creating video generation agent...")
    media_agent = create_media_creator(model_name='models/veo-3.1-generate-preview')

    # Step 2: Generate video
    prompt = "A futuristic city skyline at sunset with flying cars and neon lights"
    video_data = media_agent.create_video(prompt=prompt)

    print(f"\nVideo generated:")
    print(f"  File: {video_data['file_path']}")
    print(f"  Type: {video_data['mime_type']}")
    print(f"  Size: {video_data['size_bytes'] / 1024 / 1024:.2f} MB")

    # Step 3: Save to Django model
    # Get or create a campaign and post
    campaign, _ = Campaign.objects.get_or_create(
        campaign_id="test_video_campaign",
        defaults={
            'name': "Video Test Campaign",
            'description': "Testing video generation",
            'phase': "testing"
        }
    )

    post, _ = Post.objects.get_or_create(
        post_id="test_video_post",
        campaign=campaign,
        defaults={
            'title': "Test Video Post",
            'description': "Testing video variant",
            'phase': "Phase 1",
            'status': "draft"
        }
    )

    # Create or update content variant with video
    variant, created = ContentVariant.objects.get_or_create(
        post=post,
        variant_id='VIDEO',
        defaults={
            'content': f"Video for: {prompt}",
            'platform': 'X',
        }
    )

    # Save the video file to the variant's asset field
    with open(video_data['file_path'], 'rb') as f:
        variant.asset.save(
            f"video_{post.post_id}.mp4",
            File(f),
            save=True
        )

    print(f"\n✅ Video saved to database!")
    print(f"   Campaign: {campaign.campaign_id}")
    print(f"   Post: {post.post_id}")
    print(f"   Variant: {variant.variant_id}")
    print(f"   Asset URL: {variant.asset.url if variant.asset else 'N/A'}")

    # Optional: Clean up the temporary file after saving to database
    # import os
    # os.remove(video_data['file_path'])
    # print(f"\n🧹 Cleaned up temporary file")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("MEDIA_GEMINI_API_KEY"):
        print("❌ ERROR: MEDIA_GEMINI_API_KEY not found in environment variables!")
        print("\nPlease add MEDIA_GEMINI_API_KEY to your .env file")
        sys.exit(1)

    print("✅ API Key found!")
    print("\n" + "=" * 80)
    print("🎬 Video Generation Example")
    print("=" * 80 + "\n")

    example_video_generation()

    print("\n" + "=" * 80)
    print("✅ Example complete!")
    print("=" * 80 + "\n")
