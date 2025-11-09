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
from .content_creator import create_content_creator, save_content_variants_for_post
from .media_creator import create_media_creator
from .mermaid_parser import parse_mermaid_diagram
from .mini_strategy_agent import create_mini_strategy_agent
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


def generate_new_post_background(selected_post_pks: list, user_prompt: str):
	"""
	Background task to generate a new post based on selected posts.

	This function:
	1. Validates all selected posts belong to the same campaign
	2. Gets campaign strategy and selected posts context
	3. Executes MiniStrategyAgent to generate new post (title, description, phase)
	4. Creates new Post record
	5. Connects selected posts to new post via next_posts M2M
	6. Executes ContentCreatorAgent to generate A/B variants
	7. Saves content variants with media assets

	Args:
		selected_post_pks: List of Post primary keys to base new post on
		user_prompt: User's requested modifications or direction
	"""
	# IMPORTANT: Close any existing database connections
	connection.close()

	try:
		# Step 1: Get selected posts with retry
		def get_selected_posts():
			return list(
				Post.objects.filter(pk__in=selected_post_pks)
				.select_related('campaign')
				.prefetch_related('variants')
				.order_by('phase', 'post_id')
			)

		selected_posts = retry_on_db_lock(get_selected_posts)

		if not selected_posts:
			print(f"Error: No posts found for PKs {selected_post_pks}")
			return

		# Step 2: Validate all posts belong to same campaign
		campaigns = set(post.campaign.campaign_id for post in selected_posts)
		if len(campaigns) > 1:
			print(f"Error: Selected posts belong to different campaigns: {campaigns}")
			return

		# Step 3: Get campaign and strategy
		campaign = selected_posts[0].campaign
		campaign_strategy = campaign.strategy or "No strategy defined"

		# Step 4: Build context for MiniStrategyAgent
		selected_posts_context = []
		for post in selected_posts:
			variants = post.variants.all()
			variant_a = variants.filter(variant_id='A').first()
			variant_b = variants.filter(variant_id='B').first()

			post_context = f"""Title: "{post.title}"
Description: "{post.description}"
Phase: {post.phase}"""

			if variant_a:
				post_context += f"\nVariant A: \"{variant_a.content}\""
			if variant_b:
				post_context += f"\nVariant B: \"{variant_b.content}\""

			selected_posts_context.append(post_context)

		selected_posts_context_str = "\n\n".join([
			f"{i+1}. {ctx}" for i, ctx in enumerate(selected_posts_context)
		])

		# Step 5: Determine current phases
		phases = [post.phase for post in selected_posts]
		unique_phases = list(set(phases))
		phase_map = {"Phase 1": 1, "Phase 2": 2, "Phase 3": 3}
		max_phase_num = max(phase_map.get(p, 1) for p in unique_phases)
		current_phase = f"Phase {max_phase_num}"
		next_phase = f"Phase {min(max_phase_num + 1, 3)}"

		current_phases_info = f"""Selected posts are in phases: {', '.join(unique_phases)}
You can choose "{current_phase}" (current) or "{next_phase}" (next phase)."""

		# Step 6: Initialize MiniStrategyAgent (outside transaction)
		mini_strategy_agent = create_mini_strategy_agent()

		# Step 7: Execute MiniStrategyAgent
		print(f"Generating new post strategy for campaign {campaign.campaign_id}...")
		strategy_output = mini_strategy_agent.execute(
			selected_posts_context=selected_posts_context_str,
			campaign_strategy=campaign_strategy,
			user_prompt=user_prompt,
			current_phases=current_phases_info
		)

		print(f"New post strategy: {strategy_output.title} (Phase: {strategy_output.phase})")

		# Step 8: Create new Post with retry
		def create_new_post():
			with transaction.atomic():
				# Generate unique post_id
				post_count = Post.objects.filter(campaign=campaign).count()
				new_post_id = f"post_{campaign.campaign_id}_{post_count + 1}"

				return Post.objects.create(
					post_id=new_post_id,
					campaign=campaign,
					title=strategy_output.title,
					description=strategy_output.description,
					phase=strategy_output.phase,
					status='draft'
				)

		new_post = retry_on_db_lock(create_new_post)
		print(f"Created new post: {new_post.post_id}")

		# Step 9: Connect selected posts to new post via next_posts M2M
		def connect_posts():
			with transaction.atomic():
				for selected_post in selected_posts:
					selected_post.next_posts.add(new_post)

		retry_on_db_lock(connect_posts)
		print(f"Connected {len(selected_posts)} posts to new post")

		# Step 10: Initialize agents for content generation (outside transaction)
		content_agent = create_content_creator()
		media_agent = create_media_creator(model_name='models/gemini-2.5-flash-image')

		# Step 11: Generate A/B content (outside transaction)
		print(f"Generating A/B content for new post...")
		content_output = content_agent.execute(
			title=new_post.title,
			description=new_post.description,
			product_info=campaign.description
		)

		# Step 12: Save content variants with media
		print(f"Saving content variants with media...")
		variant_a, variant_b = save_content_variants_for_post(
			post=new_post,
			content_output=content_output,
			media_agent=media_agent,
			retry_on_db_lock=retry_on_db_lock
		)

		print(f"New post generation complete: {new_post.post_id}")
		print(f"  - Variant A: {content_output.A[:50]}...")
		print(f"  - Variant B: {content_output.B[:50]}...")

	except Exception as e:
		print(f"Error in background new post generation: {e}")
		import traceback
		traceback.print_exc()

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


class GenerateNewPostAPIView(APIView):
	"""
	API endpoint for generating new posts based on selected posts.

	POST /api/agents/generate-new-post/
	Request body:
		{
			"nodes": [1, 2, 3],  # List of Post PKs
			"prompt": "Create a follow-up post asking for beta testers"
		}

	Response:
		{
			"success": true,
			"message": "New post generation started"
		}
	"""

	def post(self, request):
		"""
		Generate a new post based on selected posts and user prompt.

		This endpoint:
		1. Validates input (nodes list and prompt)
		2. Launches background task to generate new post
		3. Returns immediately with status
		"""
		# Extract and validate input
		nodes = request.data.get('nodes')
		prompt = request.data.get('prompt')

		# Validation
		if not nodes or not isinstance(nodes, list):
			return Response(
				{
					"success": False,
					"message": "Missing or invalid 'nodes' field. Must be a list of Post PKs."
				},
				status=status.HTTP_400_BAD_REQUEST
			)

		if not prompt or not isinstance(prompt, str):
			return Response(
				{
					"success": False,
					"message": "Missing or invalid 'prompt' field. Must be a string."
				},
				status=status.HTTP_400_BAD_REQUEST
			)

		# Validate that nodes exist
		try:
			existing_posts = Post.objects.filter(pk__in=nodes)
			if existing_posts.count() != len(nodes):
				return Response(
					{
						"success": False,
						"message": f"Some posts not found. Requested {len(nodes)}, found {existing_posts.count()}."
					},
					status=status.HTTP_400_BAD_REQUEST
				)
		except Exception as e:
			return Response(
				{
					"success": False,
					"message": f"Error validating posts: {str(e)}"
				},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			# Launch background task
			new_post_thread = threading.Thread(
				target=generate_new_post_background,
				args=(nodes, prompt),
				daemon=True
			)
			new_post_thread.start()

			return Response(
				{
					"success": True,
					"message": "New post generation started",
					"selected_posts": len(nodes)
				},
				status=status.HTTP_202_ACCEPTED
			)

		except Exception as e:
			return Response(
				{
					"success": False,
					"message": f"Error starting new post generation: {str(e)}",
					"error": str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
