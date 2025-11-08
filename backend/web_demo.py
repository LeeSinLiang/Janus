#!/usr/bin/env python
"""
Janus Web Demo - Simple Flask app to visualize generated content and images
"""

import base64
import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "janus.settings")
import django
django.setup()

from agents.strategy_planner import create_strategy_planner
from agents.content_creator import create_content_creator, create_video_content_creator
from agents.media_creator import create_media_creator
from agents.models import Campaign, Post, ContentVariant
from agents.mermaid_parser import parse_mermaid_diagram
from django.core.files.base import ContentFile
from django.core.files import File

app = Flask(__name__)

# Store results in memory for display
demo_results = {
    'campaign': None,
    'posts': []
}


def run_demo(product_description: str, gtm_goals: str, enable_video: bool = False):
    """Run the demo and store results

    Args:
        product_description: Product description
        gtm_goals: GTM goals
        enable_video: If True, generate videos for Variant B instead of images
    """
    global demo_results
    demo_results = {'campaign': None, 'posts': []}

    # Scenario 1: Strategy Planning
    print("📋 Creating strategy...")
    strategy_agent = create_strategy_planner()
    strategy_output = strategy_agent.execute(product_description, gtm_goals)
    mermaid_diagram = strategy_output.diagram

    parsed_data = parse_mermaid_diagram(mermaid_diagram)

    # Create campaign
    campaign = Campaign.objects.create(
        campaign_id=f"campaign_{Campaign.objects.count() + 1}",
        name="GTM Campaign",
        description=product_description,
        strategy=mermaid_diagram,
        phase="strategizing"
    )

    # Create posts from nodes
    node_to_post = {}
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

    # Link posts
    for connection in parsed_data['connections']:
        from_node = connection['from']
        to_node = connection['to']
        if from_node in node_to_post and to_node in node_to_post:
            from_post = node_to_post[from_node]
            to_post = node_to_post[to_node]
            from_post.next_posts.add(to_post)

    print(f"✅ Created campaign with {campaign.posts.count()} posts")

    # Scenario 2: Generate A/B Content (first 3 posts)
    print("✍️  Generating A/B content...")

    # Choose content agent based on video flag
    if enable_video:
        print("🎬 Using VideoContentCreatorAgent (Variant B will have video)")
        content_agent = create_video_content_creator()
        media_agent_image = create_media_creator(model_name='models/gemini-2.5-flash-image')
        media_agent_video = create_media_creator(model_name='models/veo-3.1-generate-preview')
    else:
        print("🖼️  Using ContentCreatorAgent (both variants will have images)")
        content_agent = create_content_creator()
        media_agent_image = create_media_creator(model_name='models/gemini-2.5-flash-image')

    posts = campaign.posts.all().order_by('phase', 'post_id')[:3]

    for i, post in enumerate(posts, 1):
        print(f"Processing post {i}/{posts.count()}: {post.title}")

        post_data = {
            'post_id': post.post_id,
            'title': post.title,
            'description': post.description,
            'phase': post.phase,
            'variants': []
        }

        # Generate A/B content
        content_output = content_agent.execute(
            title=post.title,
            description=post.description,
            product_info=product_description
        )

        # Variant A (always image)
        variant_a = ContentVariant.objects.create(
            post=post,
            variant_id='A',
            content=content_output.A,
            platform='X',
        )

        print(f"  Generating image A...")
        asset_a = media_agent_image.create_image(prompt=content_output.A_image_caption)
        mime_type_a = asset_a['mime_type']
        ext_a = mime_type_a.split('/')[-1]
        data_a = ContentFile(base64.b64decode(asset_a['data']))
        variant_a.asset.save(f'variant_a_image.{ext_a}', data_a, save=True)
        variant_a.save()

        post_data['variants'].append({
            'variant_id': 'A',
            'content': content_output.A,
            'media_type': 'image',
            'media_caption': content_output.A_image_caption,
            'media_data': f"data:{mime_type_a};base64,{asset_a['data']}"
        })

        # Variant B (image or video based on enable_video flag)
        variant_b = ContentVariant.objects.create(
            post=post,
            variant_id='B',
            content=content_output.B,
            platform='X',
        )

        if enable_video:
            # Generate video for Variant B
            print(f"  Generating video B...")
            video_caption = content_output.B_video_caption
            video_data = media_agent_video.create_video(prompt=video_caption)

            # Save video file to variant
            with open(video_data['file_path'], 'rb') as f:
                variant_b.asset.save(f'variant_b_video.mp4', File(f), save=True)
            variant_b.save()

            # Convert video to base64 for display
            with open(video_data['file_path'], 'rb') as f:
                video_bytes = f.read()
                video_base64 = base64.b64encode(video_bytes).decode('utf-8')

            post_data['variants'].append({
                'variant_id': 'B',
                'content': content_output.B,
                'media_type': 'video',
                'media_caption': video_caption,
                'media_data': f"data:video/mp4;base64,{video_base64}",
                'file_size_mb': video_data['size_bytes'] / 1024 / 1024
            })

            # Clean up temp file
            import os
            os.remove(video_data['file_path'])
            print(f"  ✅ Cleaned up temp video file")
        else:
            # Generate image for Variant B
            print(f"  Generating image B...")
            asset_b = media_agent_image.create_image(prompt=content_output.B_image_caption)
            mime_type_b = asset_b['mime_type']
            ext_b = mime_type_b.split('/')[-1]
            data_b = ContentFile(base64.b64decode(asset_b['data']))
            variant_b.asset.save(f'variant_b_image.{ext_b}', data_b, save=True)
            variant_b.save()

            post_data['variants'].append({
                'variant_id': 'B',
                'content': content_output.B,
                'media_type': 'image',
                'media_caption': content_output.B_image_caption,
                'media_data': f"data:{mime_type_b};base64,{asset_b['data']}"
            })

        demo_results['posts'].append(post_data)
        print(f"  ✅ Generated variants for: {post.title}")

    demo_results['campaign'] = {
        'campaign_id': campaign.campaign_id,
        'name': campaign.name,
        'description': campaign.description,
        'total_posts': campaign.posts.count(),
        'strategy': mermaid_diagram
    }

    print("✅ Demo complete!")


@app.route('/')
def index():
    """Main page"""
    return render_template('demo.html')


@app.route('/run', methods=['POST'])
def run():
    """Run the demo with provided inputs"""
    data = request.json
    product_description = data.get('product_description',
        "Janus is an AI-powered GTM Operating System designed for technical founders. "
        "It automates marketing strategy planning, content creation with A/B testing, "
        "and metrics-driven optimization across social platforms like X and ProductHunt."
    )
    gtm_goals = data.get('gtm_goals',
        "Launch product and acquire first 100 users in 4 weeks using X and ProductHunt"
    )
    enable_video = data.get('enable_video', False)

    try:
        run_demo(product_description, gtm_goals, enable_video)
        return jsonify({'status': 'success', 'results': demo_results})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/results')
def results():
    """Get current results"""
    return jsonify(demo_results)


if __name__ == '__main__':
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables!")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Google API key to .env")
        print("3. Run the demo again")
        sys.exit(1)

    print("✅ Google API Key found!")
    print("\n" + "=" * 80)
    print("🚀 Starting Janus Web Demo")
    print("=" * 80)
    print("\nOpen your browser to: http://localhost:5000")
    print("\n" + "=" * 80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
