# Janus Agents API Documentation

This document describes the RESTful API endpoints for the Janus multi-agent system.

## Base URL

```
http://localhost:8000/api/agents/
```

---

## Endpoints

### 1. Strategy Planning

Generate a marketing strategy with Mermaid diagram and save to database.

**Endpoint:** `POST /api/agents/strategy/`

**Request Body:**

```json
{
  "product_description": "Your product description",
  "gtm_goals": "Your go-to-market goals",
  "campaign_name": "Campaign Name (optional, default: 'GTM Campaign')",
  "save_to_db": true
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_description` | string | Yes | Description of your product or service |
| `gtm_goals` | string | Yes | Go-to-market goals and objectives |
| `campaign_name` | string | No | Name for the campaign (default: "GTM Campaign") |
| `save_to_db` | boolean | No | Whether to save strategy to database (default: true) |

**Success Response (201 Created or 200 OK):**

```json
{
  "success": true,
  "campaign_id": "campaign_1",
  "mermaid_diagram": "graph TB\n    subgraph \"Phase 1\"...",
  "nodes": [
    {
      "id": "NODE1",
      "title": "Build Landing Page",
      "description": "Create compelling landing page",
      "phase": "Phase 1"
    }
  ],
  "connections": [
    {
      "from_node": "NODE1",
      "to_node": "NODE2"
    }
  ],
  "total_posts": 10,
  "message": "Strategy created successfully and saved as campaign campaign_1"
}
```

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "errors": {
    "product_description": ["This field is required."]
  },
  "message": "Invalid request data"
}
```

**Error Response (500 Internal Server Error):**

```json
{
  "success": false,
  "message": "Error generating strategy: [error details]",
  "error": "[error details]"
}
```

**Example cURL:**

```bash
curl -X POST http://localhost:8000/api/agents/strategy/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_description": "AI-powered GTM OS for technical founders",
    "gtm_goals": "Launch and get 100 users in 4 weeks",
    "campaign_name": "Launch Campaign",
    "save_to_db": true
  }'
```

**Example Python (requests):**

```python
import requests

response = requests.post(
    'http://localhost:8000/api/agents/strategy/',
    json={
        'product_description': 'AI-powered GTM OS for technical founders',
        'gtm_goals': 'Launch and get 100 users in 4 weeks',
        'campaign_name': 'Launch Campaign',
        'save_to_db': True
    }
)

data = response.json()
print(f"Campaign ID: {data['campaign_id']}")
print(f"Total Posts: {data['total_posts']}")
```

**Example JavaScript (fetch):**

```javascript
fetch('http://localhost:8000/api/agents/strategy/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_description: 'AI-powered GTM OS for technical founders',
    gtm_goals: 'Launch and get 100 users in 4 weeks',
    campaign_name: 'Launch Campaign',
    save_to_db: true
  })
})
.then(response => response.json())
.then(data => {
  console.log('Campaign ID:', data.campaign_id);
  console.log('Mermaid Diagram:', data.mermaid_diagram);
});
```

---

### 2. List Campaigns

Get a list of all campaigns.

**Endpoint:** `GET /api/agents/campaigns/`

**Success Response (200 OK):**

```json
{
  "success": true,
  "count": 5,
  "campaigns": [
    {
      "id": 1,
      "campaign_id": "campaign_1",
      "name": "Launch Campaign",
      "description": "AI-powered GTM OS for technical founders",
      "phase": "planning",
      "strategy": "graph TB...",
      "metadata": {
        "gtm_goals": "Launch and get 100 users in 4 weeks",
        "total_nodes": 10,
        "total_connections": 12
      },
      "insights": [],
      "posts_count": 10,
      "created_at": "2025-11-08T12:00:00Z",
      "updated_at": "2025-11-08T12:00:00Z"
    }
  ]
}
```

**Example cURL:**

```bash
curl http://localhost:8000/api/agents/campaigns/
```

**Example Python:**

```python
import requests

response = requests.get('http://localhost:8000/api/agents/campaigns/')
data = response.json()

print(f"Total campaigns: {data['count']}")
for campaign in data['campaigns']:
    print(f"- {campaign['campaign_id']}: {campaign['name']}")
```

---

### 3. Campaign Details

Get detailed information about a specific campaign including all posts.

**Endpoint:** `GET /api/agents/campaigns/<campaign_id>/`

**URL Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `campaign_id` | string | The campaign ID (e.g., "campaign_1") |

**Success Response (200 OK):**

```json
{
  "success": true,
  "campaign": {
    "id": 1,
    "campaign_id": "campaign_1",
    "name": "Launch Campaign",
    "description": "AI-powered GTM OS for technical founders",
    "phase": "planning",
    "strategy": "graph TB...",
    "metadata": {...},
    "insights": [],
    "posts_count": 10,
    "created_at": "2025-11-08T12:00:00Z",
    "updated_at": "2025-11-08T12:00:00Z"
  },
  "posts": [
    {
      "id": 1,
      "post_id": "post_NODE1",
      "campaign": 1,
      "title": "Build Landing Page",
      "description": "Create compelling landing page with clear value proposition",
      "phase": "Phase 1",
      "status": "draft",
      "selected_variant": null,
      "variants_count": 0,
      "next_posts_ids": ["post_NODE2", "post_NODE3"],
      "created_at": "2025-11-08T12:00:00Z",
      "updated_at": "2025-11-08T12:00:00Z"
    }
  ]
}
```

**Error Response (404 Not Found):**

```json
{
  "success": false,
  "message": "Campaign campaign_999 not found"
}
```

**Example cURL:**

```bash
curl http://localhost:8000/api/agents/campaigns/campaign_1/
```

**Example Python:**

```python
import requests

campaign_id = "campaign_1"
response = requests.get(f'http://localhost:8000/api/agents/campaigns/{campaign_id}/')
data = response.json()

campaign = data['campaign']
posts = data['posts']

print(f"Campaign: {campaign['name']}")
print(f"Total Posts: {len(posts)}")

# Group posts by phase
for phase in ['Phase 1', 'Phase 2', 'Phase 3']:
    phase_posts = [p for p in posts if p['phase'] == phase]
    print(f"\n{phase}: {len(phase_posts)} posts")
    for post in phase_posts:
        print(f"  - {post['title']}")
```

---

## Data Models

### Campaign

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Database primary key |
| `campaign_id` | string | Unique campaign identifier (e.g., "campaign_1") |
| `name` | string | Campaign name |
| `description` | string | Product/campaign description |
| `phase` | string | Campaign phase: "planning", "content_creation", "scheduled", "active", "analyzing", "completed" |
| `strategy` | string | Mermaid diagram representation of the strategy |
| `metadata` | object | Additional metadata (GTM goals, node counts, etc.) |
| `insights` | array | List of insights collected during the campaign |
| `posts_count` | integer | Number of posts in this campaign |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Post

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Database primary key |
| `post_id` | string | Unique post identifier (e.g., "post_NODE1") |
| `campaign` | integer | Campaign ID (foreign key) |
| `title` | string | Post title/action item |
| `description` | string | Post description |
| `phase` | string | Phase: "Phase 1", "Phase 2", or "Phase 3" |
| `status` | string | Status: "draft", "scheduled", "published", "analyzed" |
| `selected_variant` | string | Selected content variant ID (if any) |
| `variants_count` | integer | Number of content variants for this post |
| `next_posts_ids` | array | List of post IDs that follow this post |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Node

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Node identifier (e.g., "NODE1") |
| `title` | string | Short action item (3-5 words) |
| `description` | string | Brief explanation (5-10 words) |
| `phase` | string | Phase: "Phase 1", "Phase 2", or "Phase 3" |

### Connection

| Field | Type | Description |
|-------|------|-------------|
| `from_node` | string | Source node ID |
| `to_node` | string | Target node ID |

---

## Testing

### Run Django Server

```bash
cd src
python manage.py runserver
```

### Test with Python Script

```bash
# Install requests if needed
pip install requests

# Run test script
python test_strategy_api.py
```

### Test with cURL

```bash
# Create a strategy
curl -X POST http://localhost:8000/api/agents/strategy/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_description": "AI marketing automation tool",
    "gtm_goals": "Get 100 beta users in 30 days"
  }'

# List campaigns
curl http://localhost:8000/api/agents/campaigns/

# Get campaign details
curl http://localhost:8000/api/agents/campaigns/campaign_1/
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React frontend)
- `http://127.0.0.1:3000`

CORS settings are in `src/janus/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

---

## Error Handling

All endpoints return a consistent error format:

```json
{
  "success": false,
  "message": "Error description",
  "errors": {} // Optional: validation errors
}
```

HTTP status codes:
- `200 OK` - Successful GET request
- `201 Created` - Successfully created resource
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Next Steps

After creating a strategy, you can:
1. Generate A/B content for posts (coming soon)
2. Analyze metrics and optimize content (coming soon)
3. Schedule and publish posts (coming soon)

See `demo.py` for complete workflow examples.
