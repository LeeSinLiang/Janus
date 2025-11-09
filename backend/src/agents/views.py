"""
API Views for Agents
"""

import base64
import threading
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, connection
from django.db.utils import OperationalError
from django.core.files.base import ContentFile

from .serializers import (
	StrategyPlanningRequestSerializer,
	StrategyPlanningResponseSerializer,
	CampaignSerializer,
	PostSerializer
)
from .strategy_planner import create_strategy_planner
from .content_creator import create_content_creator
from .media_creator import create_media_creator
from .mermaid_parser import parse_mermaid_diagram
from .models import Campaign, Post, ContentVariant


def retry_on_db_lock(func, max_retries=5, initial_delay=0.1):
	"""
	Retry a database operation with exponential backoff if it fails due to database lock.

	Args:
		func: Function to retry
		max_retries: Maximum number of retry attempts
		initial_delay: Initial delay in seconds (will be doubled after each retry)

	Returns:
		The result of the function call

	Raises:
		OperationalError: If all retries fail
	"""
	delay = initial_delay
	last_exception = None

	for attempt in range(max_retries):
		try:
			return func()
		except OperationalError as e:
			last_exception = e
			if "database is locked" in str(e).lower():
				if attempt < max_retries - 1:
					print(f"Database locked, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
					time.sleep(delay)
					delay *= 2  # Exponential backoff
				else:
					print(f"Database locked after {max_retries} attempts, giving up")
					raise
			else:
				# Not a lock error, re-raise immediately
				raise

	# Should not reach here, but just in case
	if last_exception:
		raise last_exception


def generate_ab_content_background(campaign_id: str, product_description: str):
	"""
	Background task to generate A/B content for all posts in a campaign.

	This function:
	1. Sets campaign phase to "content_creation"
	2. Generates A/B content variants for all posts
	3. Generates media assets for each variant
	4. Sets campaign phase to "scheduled" when complete

	Args:
		campaign_id: ID of the campaign to generate content for
		product_description: Product description for content generation context
	"""
	# IMPORTANT: Close any existing database connections
	# Threads need to manage their own database connections
	connection.close()

	try:
		# Step 1: Get campaign and set phase to content_creation
		def update_campaign_phase_to_creation():
			with transaction.atomic():
				campaign = Campaign.objects.select_for_update().get(campaign_id=campaign_id)
				campaign.phase = 'content_creation'
				campaign.save(update_fields=['phase', 'updated_at'])
				return campaign

		campaign = retry_on_db_lock(update_campaign_phase_to_creation)

		# Step 2: Initialize agents (outside of database transactions)
		content_agent = create_content_creator()
		media_agent = create_media_creator(model_name='models/gemini-2.5-flash-image')

		# Step 3: Get all posts from campaign
		def get_posts():
			return list(Campaign.objects.get(campaign_id=campaign_id).posts.all().order_by('phase', 'post_id'))

		posts = retry_on_db_lock(get_posts)

		# Step 4: Generate A/B content for each post
		for post in posts:
			try:
				# Generate A/B content (outside of database transaction)
				content_output = content_agent.execute(
					title=post.title,
					description=post.description,
					product_info=product_description
				)

				# Create ContentVariant A with retry logic
				def create_variant_a():
					with transaction.atomic():
						return ContentVariant.objects.create(
							post=post,
							variant_id='A',
							content=content_output.A,
							platform='X',
							metadata={'image_caption': content_output.A_image_caption}
						)

				variant_a = retry_on_db_lock(create_variant_a)

				# Generate and save media for Variant A
				try:
					asset_a = media_agent.create_image(prompt=content_output.A_image_caption)
					mime_type = asset_a['mime_type']
					ext = mime_type.split('/')[-1]
					data = ContentFile(base64.b64decode(asset_a['data']))

					# Save asset with retry logic
					def save_variant_a_asset():
						variant_a.asset.save(f'variant_a_image.{ext}', data, save=True)

					retry_on_db_lock(save_variant_a_asset)
				except Exception as e:
					print(f"Warning: Failed to generate image for variant A of post {post.post_id}: {e}")

				# Create ContentVariant B with retry logic
				def create_variant_b():
					with transaction.atomic():
						return ContentVariant.objects.create(
							post=post,
							variant_id='B',
							content=content_output.B,
							platform='X',
							metadata={'image_caption': content_output.B_image_caption}
						)

				variant_b = retry_on_db_lock(create_variant_b)

				# Generate and save media for Variant B
				try:
					asset_b = media_agent.create_image(prompt=content_output.B_image_caption)
					mime_type = asset_b['mime_type']
					ext = mime_type.split('/')[-1]
					data = ContentFile(base64.b64decode(asset_b['data']))

					# Save asset with retry logic
					def save_variant_b_asset():
						variant_b.asset.save(f'variant_b_image.{ext}', data, save=True)

					retry_on_db_lock(save_variant_b_asset)
				except Exception as e:
					print(f"Warning: Failed to generate image for variant B of post {post.post_id}: {e}")

			except Exception as e:
				print(f"Error generating variants for post {post.post_id}: {e}")
				# Continue with next post even if one fails
				continue

		# Step 5: Set campaign phase to scheduled
		def update_campaign_phase_to_scheduled():
			with transaction.atomic():
				campaign = Campaign.objects.select_for_update().get(campaign_id=campaign_id)
				campaign.phase = 'scheduled'
				campaign.save(update_fields=['phase', 'updated_at'])

		retry_on_db_lock(update_campaign_phase_to_scheduled)

		print(f"Content generation complete for campaign {campaign_id}")

	except Exception as e:
		print(f"Error in background content generation for campaign {campaign_id}: {e}")
		import traceback
		traceback.print_exc()

		# Set campaign phase to planning if error occurs
		def rollback_campaign_phase():
			try:
				with transaction.atomic():
					campaign = Campaign.objects.select_for_update().get(campaign_id=campaign_id)
					campaign.phase = 'planning'
					campaign.save(update_fields=['phase', 'updated_at'])
			except Exception as rollback_error:
				print(f"Failed to rollback campaign phase: {rollback_error}")

		try:
			retry_on_db_lock(rollback_campaign_phase)
		except:
			pass

	finally:
		# Close database connection when thread is done
		connection.close()


class StrategyPlanningAPIView(APIView):
	"""
	API endpoint for generating marketing strategies with Mermaid diagrams.

	POST /api/agents/strategy/
	Request body:
		{
			"product_description": "Your product description",
			"gtm_goals": "Your GTM goals",
			"campaign_name": "Campaign Name" (optional, default: "GTM Campaign"),
			"save_to_db": true (optional, default: true)
		}

	Response:
		{
			"success": true,
			"campaign_id": "campaign_1",
			"mermaid_diagram": "graph TB...",
			"nodes": [...],
			"connections": [...],
			"total_posts": 10,
			"message": "Strategy created successfully"
		}
	"""

	def post(self, request):
		"""
		Generate a marketing strategy with Mermaid diagram.

		This endpoint:
		1. Validates the input (product description and GTM goals)
		2. Calls the Strategy Planner agent to generate a Mermaid diagram
		3. Parses the diagram to extract nodes and connections
		4. Optionally saves to database (Campaign + Posts)
		5. Returns the strategy data
		"""
		# Validate request data
		serializer = StrategyPlanningRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(
				{
					"success": False,
					"errors": serializer.errors,
					"message": "Invalid request data"
				},
				status=status.HTTP_400_BAD_REQUEST
			)

		# Extract validated data
		product_description = serializer.validated_data['product_description']
		gtm_goals = serializer.validated_data['gtm_goals']

		try:
			# Step 1: Generate strategy with Strategy Planner
			strategy_agent = create_strategy_planner()
			strategy_output = strategy_agent.execute(product_description, gtm_goals)
			mermaid_diagram = strategy_output.diagram

			# Step 2: Parse mermaid diagram
			parsed_data = parse_mermaid_diagram(mermaid_diagram)
			nodes = parsed_data['nodes']
			connections = parsed_data['connections']

			# Step 3: Optionally save to database
			campaign = None
			campaign_id = None

			with transaction.atomic():
				# Create campaign
				campaign = Campaign.objects.create(
					campaign_id=f"campaign_{Campaign.objects.count() + 1}",
					name=f"campaign_{Campaign.objects.count() + 1}",
					description=product_description,
					strategy=mermaid_diagram,
					phase="planning",
					metadata={
						"gtm_goals": gtm_goals,
						"total_nodes": len(nodes),
						"total_connections": len(connections)
					}
				)
				campaign_id = campaign.campaign_id

				# Create posts from nodes
				node_to_post = {}
				for node in nodes:
					post = Post.objects.create(
						post_id=f"post_{node['id']}",
						campaign=campaign,
						title=node['title'],
						description=node['description'],
						phase=node['phase'] if node['phase'] in ['Phase 1', 'Phase 2', 'Phase 3'] else 'Phase 1',
						status='draft'
					)
					node_to_post[node['id']] = post

				# Link posts based on connections
				for connection in connections:
					from_node = connection['from']
					to_node = connection['to']

					if from_node in node_to_post and to_node in node_to_post:
						from_post = node_to_post[from_node]
						to_post = node_to_post[to_node]
						from_post.next_posts.add(to_post)

			# Step 4: Prepare response
			response_data = {
				"success": True,
				"campaign_id": campaign_id,
				"mermaid_diagram": mermaid_diagram,
				"nodes": nodes,
				"connections": connections,
				"total_posts": len(nodes),
				"message": "Strategy created successfully" + (
					f" and saved as campaign {campaign_id}"
				)
			}

			# Step 5: Trigger background content generation (Scenario 2)
			# This will:
			# 1. Set campaign phase to "content_creation"
			# 2. Generate A/B content for all posts
			# 3. Set campaign phase to "scheduled" when complete
			content_thread = threading.Thread(
				target=generate_ab_content_background,
				args=(campaign_id, product_description),
				daemon=True
			)
			content_thread.start()

			return Response(
				response_data,
				status=status.HTTP_201_CREATED
			)

		except Exception as e:
			return Response(
				{
					"success": False,
					"message": f"Error generating strategy: {str(e)}",
					"error": str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class CampaignListAPIView(APIView):
	"""
	API endpoint for listing campaigns.

	GET /api/agents/campaigns/
	"""

	def get(self, request):
		"""List all campaigns"""
		campaigns = Campaign.objects.all().order_by('-created_at')
		serializer = CampaignSerializer(campaigns, many=True)
		return Response({
			"success": True,
			"count": campaigns.count(),
			"campaigns": serializer.data
		})


class CampaignDetailAPIView(APIView):
	"""
	API endpoint for campaign details.

	GET /api/agents/campaigns/<campaign_id>/
	"""

	def get(self, request, campaign_id):
		"""Get campaign details with posts"""
		try:
			campaign = Campaign.objects.get(campaign_id=campaign_id)
			campaign_serializer = CampaignSerializer(campaign)

			# Get posts for this campaign
			posts = campaign.posts.all().order_by('phase', 'post_id')
			posts_serializer = PostSerializer(posts, many=True)

			return Response({
				"success": True,
				"campaign": campaign_serializer.data,
				"posts": posts_serializer.data
			})
		except Campaign.DoesNotExist:
			return Response(
				{
					"success": False,
					"message": f"Campaign {campaign_id} not found"
				},
				status=status.HTTP_404_NOT_FOUND
			)
