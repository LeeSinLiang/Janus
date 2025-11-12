# Strategy Regeneration API Endpoint

## Overview

Django REST API endpoint for regenerating campaign strategies from a specific phase onwards. This endpoint handles database versioning, post archival, and background content generation.

## Endpoint

```
POST /api/agents/campaigns/regenerate/
```

## Request Format

```json
{
  "campaign_id": "campaign_001",
  "phase_num": 2,
  "new_direction": "Focus on ProductHunt launch with heavy emphasis on developer communities"
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `campaign_id` | string | ✅ | Unique identifier of the campaign to regenerate |
| `phase_num` | integer | ✅ | Phase number to start regeneration from (e.g., 2 = regenerate Phase 2+) |
| `new_direction` | string | ✅ | Strategic direction or reason for regeneration |

## Response Format

### Success (200 OK)

```json
{
  "status": "success",
  "message": "Strategy regenerated successfully from Phase 2",
  "data": {
    "campaign_id": "campaign_001",
    "archived_posts": 5,
    "new_posts": 8,
    "version": 2,
    "diagram_length": 1478
  }
}
```

### Error (400 Bad Request)

```json
{
  "status": "error",
  "message": "Campaign not found: campaign_001"
}
```

```json
{
  "status": "error",
  "message": "Phase number must be greater than 1"
}
```

```json
{
  "status": "error",
  "message": "No existing posts found before Phase 2"
}
```

## Backend Workflow

The endpoint executes the following steps:

### 1. Validation
- Validates `campaign_id`, `phase_num`, `new_direction`
- Checks that `phase_num > 1` (cannot regenerate Phase 1)
- Verifies campaign exists in database

### 2. Fetch Existing Data
```python
campaign = Campaign.objects.get(campaign_id=campaign_id)
existing_posts = Post.objects.filter(
    campaign=campaign,
    phase__lt=f"Phase {phase_num}",
    is_active=True
).order_by('phase', 'post_id')
```

### 3. Archive Old Posts
- Sets `is_active=False` for posts from `phase_num` onwards
- Preserves posts in database for history
- Uses database transaction for atomicity

### 4. Version Increment
```python
campaign.current_version += 1
campaign.save()
```

### 5. Strategy Regeneration
```python
strategy_agent = create_strategy_planner()
strategy_output = strategy_agent.execute_from_phase(
    phase_num=phase_num,
    existing_posts=existing_posts_formatted,
    product_description=campaign.description,
    gtm_goals=campaign.metadata.get('gtm_goals'),
    new_direction=new_direction
)
```

### 6. Parse Mermaid Diagram
```python
parsed_data = parse_mermaid_diagram(strategy_output.diagram)
nodes = parsed_data['nodes']
connections = parsed_data['connections']
```

### 7. Create New Post Objects
```python
for node in nodes:
    if node['phase'] >= phase_num:  # Only create new phase posts
        Post.objects.create(
            campaign=campaign,
            post_id=f"post_{node['node_id']}",
            title=node['title'],
            description=node['description'],
            phase=node['phase'],
            version=campaign.current_version,
            is_active=True,
            status='draft'
        )
```

### 8. Link Posts (Many-to-Many)
```python
for connection in connections:
    from_post = Post.objects.get(post_id=f"post_{connection['from']}")
    to_post = Post.objects.get(post_id=f"post_{connection['to']}")
    from_post.next_posts.add(to_post)
```

### 9. Update Campaign Strategy
```python
campaign.strategy = strategy_output.diagram
campaign.save()
```

### 10. Background Content Generation
```python
# Launch thread to generate A/B content for new posts
thread = threading.Thread(
    target=generate_content_for_posts,
    args=(campaign, new_posts)
)
thread.daemon = True
thread.start()
```

## Database Schema

### Campaign Model

```python
class Campaign(models.Model):
    campaign_id = models.CharField(max_length=255, unique=True)
    current_version = models.IntegerField(default=1)
    strategy = models.TextField(blank=True)  # Mermaid diagram
    metadata = models.JSONField(default=dict)  # Contains gtm_goals
```

### Post Model

```python
class Post(models.Model):
    post_id = models.CharField(max_length=255, unique=True)
    campaign = models.ForeignKey(Campaign)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    phase = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    description = models.TextField()
    status = models.CharField(max_length=50)
    next_posts = models.ManyToManyField('self', symmetrical=False)
```

## Usage Examples

### Example 1: cURL Request

```bash
curl -X POST http://localhost:8000/api/agents/campaigns/regenerate/ \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign_001",
    "phase_num": 2,
    "new_direction": "Pivot to developer-first strategy with ProductHunt emphasis"
  }'
```

### Example 2: JavaScript (Fetch API)

```javascript
const response = await fetch('http://localhost:8000/api/agents/campaigns/regenerate/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    campaign_id: 'campaign_001',
    phase_num: 2,
    new_direction: 'Focus on technical content and developer influencers'
  })
});

const result = await response.json();
console.log(`Archived ${result.data.archived_posts} posts`);
console.log(`Created ${result.data.new_posts} new posts`);
```

### Example 3: Python (Requests)

```python
import requests

response = requests.post(
    'http://localhost:8000/api/agents/campaigns/regenerate/',
    json={
        'campaign_id': 'campaign_001',
        'phase_num': 3,
        'new_direction': 'Scale with content marketing and partnerships'
    }
)

data = response.json()
print(f"Status: {data['status']}")
print(f"New version: {data['data']['version']}")
```

### Example 4: Frontend Integration (React)

```typescript
import { api } from '@/services/api';

async function regenerateCampaign(
  campaignId: string,
  phaseNum: number,
  newDirection: string
) {
  try {
    const response = await api.post('/api/agents/campaigns/regenerate/', {
      campaign_id: campaignId,
      phase_num: phaseNum,
      new_direction: newDirection
    });

    if (response.data.status === 'success') {
      console.log(`✓ Regenerated from Phase ${phaseNum}`);
      console.log(`✓ Created ${response.data.data.new_posts} new posts`);
      // Trigger UI refresh to show new campaign structure
      await refreshCampaignData(campaignId);
    }
  } catch (error) {
    console.error('Regeneration failed:', error);
  }
}
```

## Versioning System

The API implements a versioning system to track strategy iterations:

### Version Tracking

- Each campaign starts at `current_version=1`
- Every regeneration increments the version
- Posts store their creation version in `Post.version`
- Old posts are marked `is_active=False` (soft delete)

### Querying Active Posts

```python
# Get current strategy posts only
active_posts = Post.objects.filter(
    campaign=campaign,
    is_active=True
)

# Get all posts from a specific version
version_2_posts = Post.objects.filter(
    campaign=campaign,
    version=2
)

# Get post history timeline
all_versions = Post.objects.filter(
    campaign=campaign
).order_by('version', 'created_at')
```

### Version Rollback (Not Yet Implemented)

Future enhancement to revert to previous version:

```python
# Pseudocode for rollback
def rollback_to_version(campaign_id, target_version):
    # Deactivate current posts
    Post.objects.filter(
        campaign_id=campaign_id,
        is_active=True
    ).update(is_active=False)

    # Reactivate target version posts
    Post.objects.filter(
        campaign_id=campaign_id,
        version=target_version
    ).update(is_active=True)

    # Update campaign metadata
    campaign.current_version = target_version
    campaign.save()
```

## Background Content Generation

After creating new posts, the API launches a background thread to generate A/B content variants:

```python
def generate_content_for_posts(campaign, posts):
    """
    Background task that generates A/B content variants for new posts.
    """
    content_agent = create_content_creator()

    for post in posts:
        if post.status == 'draft' and post.is_active:
            # Generate A/B variants
            result = content_agent.execute(
                title=post.title,
                description=post.description,
                product_info=campaign.description
            )

            # Save variants to database
            save_content_variants_for_post(
                post_id=post.post_id,
                content_a=result.A,
                content_b=result.B,
                platform='x'
            )

            # Update post status
            post.status = 'pending_review'
            post.save()
```

**Notes:**
- Content generation happens asynchronously
- API returns immediately (doesn't wait for content)
- Frontend polls for updates via `/nodesJson/` endpoint
- Only generates content for `draft` posts with `is_active=True`

## Error Handling

The endpoint includes comprehensive error handling:

```python
try:
    # Validation errors
    if not campaign_id or not new_direction:
        return Response({
            'status': 'error',
            'message': 'Missing required fields'
        }, status=400)

    if phase_num <= 1:
        return Response({
            'status': 'error',
            'message': 'Phase number must be greater than 1'
        }, status=400)

    # Database errors
    campaign = Campaign.objects.get(campaign_id=campaign_id)

except Campaign.DoesNotExist:
    return Response({
        'status': 'error',
        'message': f'Campaign not found: {campaign_id}'
    }, status=404)

except Exception as e:
    logger.error(f"Regeneration error: {str(e)}")
    return Response({
        'status': 'error',
        'message': f'Internal error: {str(e)}'
    }, status=500)
```

## Testing

### Manual API Testing

```bash
# 1. Create a campaign first
curl -X POST http://localhost:8000/api/agents/strategy/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_description": "AI-powered GTM OS",
    "gtm_goals": "Launch and acquire 100 users"
  }'

# 2. Wait for Phase 1 posts to be created

# 3. Regenerate from Phase 2
curl -X POST http://localhost:8000/api/agents/campaigns/regenerate/ \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign_001",
    "phase_num": 2,
    "new_direction": "Pivot to developer communities"
  }'

# 4. Check updated campaign
curl http://localhost:8000/nodesJson/?campaign_id=campaign_001
```

### Django Test Case

```python
from django.test import TestCase
from rest_framework.test import APIClient

class StrategyRegenerationTest(TestCase):
    def test_regenerate_from_phase_2(self):
        client = APIClient()

        # Create campaign with Phase 1 posts
        # ... setup code ...

        # Regenerate
        response = client.post('/api/agents/campaigns/regenerate/', {
            'campaign_id': 'test_campaign',
            'phase_num': 2,
            'new_direction': 'New strategy'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertGreater(response.data['data']['new_posts'], 0)
```

## Security Considerations

### Authentication (Not Yet Implemented)

Future enhancements should include:
- User authentication required
- Campaign ownership validation
- Rate limiting on regenerations
- Audit logging of strategy changes

### Input Validation

Current validations:
- ✅ Campaign existence check
- ✅ Phase number validation (must be > 1)
- ✅ Required fields check
- ✅ Database transaction rollback on errors

### Resource Limits

Consider adding:
- Max regenerations per day
- Max campaign versions to keep
- Background task timeout
- Content generation queue limits

## Related Documentation

- [Strategy Regeneration Feature](/home/sllee/coding/aiatl/backend/STRATEGY_REGENERATION.md) - Core feature documentation
- [Strategy Planner Agent](/home/sllee/coding/aiatl/backend/src/agents/strategy_planner.py) - Implementation
- [Campaign Views](/home/sllee/coding/aiatl/backend/src/agents/views.py) - Full API endpoint code
- [Models Schema](/home/sllee/coding/aiatl/backend/src/agents/models.py) - Database models

## Changelog

- **v1.0** (2025-01-11): Initial implementation with versioning and archival system
- Added `execute_from_phase()` method to strategy planner
- Implemented many-to-many connection support
- Added background content generation
