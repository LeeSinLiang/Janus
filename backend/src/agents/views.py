"""
API Views for Agents
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .serializers import (
    StrategyPlanningRequestSerializer,
    StrategyPlanningResponseSerializer,
    CampaignSerializer,
    PostSerializer
)
from .strategy_planner import create_strategy_planner
from .mermaid_parser import parse_mermaid_diagram
from .models import Campaign, Post


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
        campaign_name = serializer.validated_data.get('campaign_name', 'GTM Campaign')
        save_to_db = serializer.validated_data.get('save_to_db', True)

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

            if save_to_db:
                with transaction.atomic():
                    # Create campaign
                    campaign = Campaign.objects.create(
                        campaign_id=f"campaign_{Campaign.objects.count() + 1}",
                        name=campaign_name,
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
                    f" and saved as campaign {campaign_id}" if save_to_db else ""
                )
            }

            return Response(
                response_data,
                status=status.HTTP_201_CREATED if save_to_db else status.HTTP_200_OK
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
