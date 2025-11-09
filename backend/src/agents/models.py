from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json

from metrics.models import PostMetrics


class Campaign(models.Model):
	"""Marketing campaign with phases, strategy, and posts"""

	PHASE_CHOICES = [
		('planning', 'Planning'),
		('content_creation', 'Content Creation'),
		('scheduled', 'Scheduled'),
		('active', 'Active'),
		('analyzing', 'Analyzing'),
		('completed', 'Completed'),
	]

	campaign_id = models.CharField(max_length=255, unique=True, db_index=True)
	name = models.CharField(max_length=255)
	description = models.TextField()
	phase = models.CharField(max_length=50, choices=PHASE_CHOICES, default='planning')

	# Store Mermaid diagram
	strategy = models.TextField(blank=True, null=True, help_text="Mermaid diagram representation")

	# Store metadata and insights as JSON
	metadata = models.JSONField(default=dict, blank=True)
	insights = models.JSONField(default=list, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['campaign_id']),
			models.Index(fields=['phase']),
			models.Index(fields=['-created_at']),
		]

	def __str__(self):
		return f"{self.name} ({self.campaign_id})"

	def add_insight(self, insight: str):
		"""Add an insight to the campaign"""
		if not isinstance(self.insights, list):
			self.insights = []
		self.insights.append(insight)
		self.save(update_fields=['insights', 'updated_at'])


class Post(models.Model):
	"""Post with A/B variants and metrics"""

	STATUS_CHOICES = [
		('draft', 'Draft'),
		('scheduled', 'Scheduled'),
		('published', 'Published'),
		('analyzed', 'Analyzed'),
	]

	PHASE_CHOICES = [
		('Phase 1', 'Phase 1'),
		('Phase 2', 'Phase 2'),
		('Phase 3', 'Phase 3'),
	]

	post_id = models.CharField(max_length=255, blank=False, null=True)
	campaign = models.ForeignKey(
		Campaign,
		on_delete=models.CASCADE,
		related_name='posts'
	)

	title = models.CharField(max_length=500, default='')
	description = models.TextField(default='')
	phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default='Phase 1')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	selected_variant = models.CharField(max_length=10, blank=True, null=True)

	metrics = models.ForeignKey(PostMetrics, on_delete=models.SET_NULL, null=True, blank=True)
	trigger = models.CharField(max_length=255, blank=True, null=True)

	# Many-to-many relationship to track post dependencies
	next_posts = models.ManyToManyField(
		'self',
		blank=True,
		symmetrical=False,
		related_name='previous_posts'
	)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['post_id']),
			models.Index(fields=['campaign', 'status']),
			models.Index(fields=['-created_at']),
		]

	def __str__(self):
		return f"Post {self.title} - {self.campaign.name}"

	# create metrics object when create new post
	def save(self, *args, **kwargs):
		if not self.metrics:
			metrics = PostMetrics.objects.create(
				likes=0,
				impressions=0,
				retweets=0,
			)
			self.metrics = metrics
		super().save(*args, **kwargs)


class ContentVariant(models.Model):
	"""Individual content variant (A or B)"""

	PLATFORM_CHOICES = [
		('X', 'X'),
	]

	variant_id = models.CharField(max_length=50)
	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE,
		related_name='variants'
	)

	content = models.TextField()
	platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='X')
	asset = models.FileField(upload_to='content_variants/', blank=True, null=True)

	# Store metadata (hook, reasoning, hashtags, etc.) as JSON
	metadata = models.JSONField(default=dict, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['variant_id']
		unique_together = [['post', 'variant_id']]
		indexes = [
			models.Index(fields=['post', 'variant_id']),
		]

	def __str__(self):
		return f"Variant {self.variant_id} - {self.post.post_id}"


class AgentMemory(models.Model):
	"""Memory storage for individual agents"""

	agent_name = models.CharField(max_length=100, unique=True, db_index=True)

	# Store context and history as JSON
	context = models.JSONField(default=dict, blank=True)
	history = models.JSONField(default=list, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name_plural = "Agent Memories"
		indexes = [
			models.Index(fields=['agent_name']),
		]

	def __str__(self):
		return f"Memory: {self.agent_name}"

	def add_to_history(self, entry: dict):
		"""Add entry to agent history"""
		if not isinstance(self.history, list):
			self.history = []
		from datetime import datetime
		entry['timestamp'] = datetime.now().isoformat()
		self.history.append(entry)
		self.save(update_fields=['history', 'updated_at'])

	def update_context(self, context_update: dict):
		"""Update agent context"""
		if not isinstance(self.context, dict):
			self.context = {}
		self.context.update(context_update)
		self.save(update_fields=['context', 'updated_at'])


class ConversationMessage(models.Model):
	"""Conversation history storage"""

	ROLE_CHOICES = [
		('user', 'User'),
		('assistant', 'Assistant'),
		('system', 'System'),
	]

	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	content = models.TextField()
	metadata = models.JSONField(default=dict, blank=True)

	# Optional link to campaign
	campaign = models.ForeignKey(
		Campaign,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='conversations'
	)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['created_at']
		indexes = [
			models.Index(fields=['created_at']),
			models.Index(fields=['campaign', 'created_at']),
		]

	def __str__(self):
		return f"{self.role}: {self.content[:50]}..."


if __name__ == "__main__":
	# Simple test to create a campaign and a post
	campaign = Campaign.objects.create(
		campaign_id="camp_001",
		name="Summer Sale",
		description="Campaign for summer sale promotion."
	)

	post = Post.objects.create(
		post_id="post_001",
		campaign=campaign,
		phase="content_creation"
	)

	variant_a = ContentVariant.objects.create(
		variant_id="A",
		post=post,
		content="Check out our summer sale! #SummerSale",
		platform="X"
	)

	variant_b = ContentVariant.objects.create(
		variant_id="B",
		post=post,
		content="Don't miss our hot summer deals! #HotDeals",
		platform="X"
	)

	node_id = post.pk
	tweet_id = post.metrics.tweet_id
	print(f"Created campaign: {campaign}")
	print(f"Created post: {post}")
	print(f"Created variant A: {variant_a}")
	print(f"Created variant B: {variant_b}")