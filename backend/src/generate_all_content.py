#!/usr/bin/env python
"""
Generate A/B content variants for all posts that don't have them yet.
Run with: python generate_all_content.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'janus.settings')
django.setup()

from agents.models import Campaign, Post, ContentVariant
from agents.content_creator import create_content_creator

def main():
    # Initialize content creator once
    print("Initializing content creator agent...")
    content_agent = create_content_creator()

    # Get all campaigns
    campaigns = Campaign.objects.all().order_by('-created_at')

    for campaign in campaigns:
        print(f"\n{'='*60}")
        print(f"Campaign: {campaign.campaign_id} ({campaign.phase})")
        print(f"Description: {campaign.description[:100]}...")
        print(f"{'='*60}")

        # Get all posts without variants
        posts = campaign.posts.all()

        for post in posts:
            # Check if post already has variants
            variant_count = ContentVariant.objects.filter(post=post).count()

            if variant_count >= 2:
                print(f"  ✓ Post {post.pk} '{post.title}' - already has {variant_count} variants")
                continue

            print(f"  → Generating content for post {post.pk}: '{post.title}'...")

            try:
                # Generate A/B content
                content_output = content_agent.execute(
                    title=post.title,
                    description=post.description,
                    product_info=campaign.description
                )

                # Create or update variant A
                variant_a, created = ContentVariant.objects.update_or_create(
                    post=post,
                    variant_id='A',
                    defaults={
                        'content': content_output.A,
                        'platform': 'X',
                        'metadata': {'image_caption': content_output.A_image_caption}
                    }
                )

                # Create or update variant B
                variant_b, created = ContentVariant.objects.update_or_create(
                    post=post,
                    variant_id='B',
                    defaults={
                        'content': content_output.B,
                        'platform': 'X',
                        'metadata': {'image_caption': content_output.B_image_caption}
                    }
                )

                print(f"    ✓ Created variants A and B")
                print(f"      Variant A: {content_output.A[:80]}...")
                print(f"      Variant B: {content_output.B[:80]}...")

            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                continue

        # Update campaign phase if all posts have variants
        total_posts = posts.count()
        posts_with_variants = sum(1 for p in posts if ContentVariant.objects.filter(post=p).count() >= 2)

        if posts_with_variants == total_posts and total_posts > 0:
            campaign.phase = 'scheduled'
            campaign.save()
            print(f"\n  ✓ Campaign phase updated to 'scheduled'")
        else:
            print(f"\n  Progress: {posts_with_variants}/{total_posts} posts have variants")

if __name__ == '__main__':
    print("Starting content generation for all campaigns...\n")
    main()
    print("\n✓ Done!")
