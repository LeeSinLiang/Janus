# A/B Metrics Architecture Migration Plan

## Overview
Refactor the metrics architecture to support A/B testing where both variants (A and B) of each post are published and tracked separately with their own metrics and tweet_ids.

## Requirements Summary
1. **Storage**: Keep everything in `PostMetrics` model (no separate model)
2. **Posting**: Both variants A and B are posted simultaneously, each gets separate `tweet_id`
3. **Backward Compatibility**: Existing posts get variant A metrics, variant B stays empty/zero
4. **Display**:
   - Canvas nodes (TaskCardNode): Show **max/winner** metrics between A and B
   - Chart view (PostMetricsBox): Show **aggregated** (A + B) metrics
   - NodeVariantModal: Show **separate** A and B metrics

5. **API Response Format**:
```json
{
  "metrics": {
    "1": {
      "A": {"likes": 100, "retweets": 50, "comments": 20, "impressions": 500},
      "B": {"likes": 120, "retweets": 45, "comments": 25, "impressions": 480}
    }
  }
}
```

---

## Phase 1: Backend Database Schema Changes

### 1.1 Update PostMetrics Model
**File**: `backend/src/metrics/models.py`

**Current Structure**:
```python
class PostMetrics(models.Model):
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    commentList = models.JSONField(default=list)
    tweet_id = models.CharField(max_length=50, blank=True, default="")
```

**New Structure**:
```python
class PostMetrics(models.Model):
    # A/B variant metrics stored as JSON
    likes = models.JSONField(default=dict)  # {"A": 100, "B": 120}
    retweets = models.JSONField(default=dict)  # {"A": 50, "B": 45}
    impressions = models.JSONField(default=dict)  # {"A": 500, "B": 480}
    comments = models.JSONField(default=dict)  # {"A": 20, "B": 25}
    commentList = models.JSONField(default=dict)  # {"A": [...], "B": [...]}
    tweet_id = models.JSONField(default=dict)  # {"A": "123", "B": "456"}

    # Helper methods for backward compatibility and convenience
    def get_variant_metrics(self, variant='A'):
        return {
            'likes': self.likes.get(variant, 0),
            'retweets': self.retweets.get(variant, 0),
            'impressions': self.impressions.get(variant, 0),
            'comments': self.comments.get(variant, 0),
        }

    def get_max_metrics(self):
        """Get maximum metrics across both variants for display"""
        return {
            'likes': max(self.likes.get('A', 0), self.likes.get('B', 0)),
            'retweets': max(self.retweets.get('A', 0), self.retweets.get('B', 0)),
            'impressions': max(self.impressions.get('A', 0), self.impressions.get('B', 0)),
            'comments': max(self.comments.get('A', 0), self.comments.get('B', 0)),
        }

    def get_aggregated_metrics(self):
        """Get sum of metrics across both variants for chart view"""
        return {
            'likes': self.likes.get('A', 0) + self.likes.get('B', 0),
            'retweets': self.retweets.get('A', 0) + self.retweets.get('B', 0),
            'impressions': self.impressions.get('A', 0) + self.impressions.get('B', 0),
            'comments': self.comments.get('A', 0) + self.comments.get('B', 0),
        }
```

**Migration Steps**:
1. Create Django migration to convert existing data
2. Convert old integer fields to JSONField with structure: `{"A": <old_value>, "B": 0}`
3. Update tweet_id from string to JSON: `{"A": "<old_tweet_id>", "B": ""}`

**Migration Command**:
```bash
python manage.py makemigrations metrics
python manage.py migrate metrics
```

---

## Phase 2: Backend API Updates

### 2.1 Update createXPost Endpoint
**File**: `backend/src/metrics/views.py:138-175`

**Changes**:
- Post **both** variant A and variant B to Twitter clone
- Store separate tweet_ids in PostMetrics as JSON: `{"A": "tweet_123", "B": "tweet_456"}`

**New Logic**:
```python
@api_view(['POST'])
def createXPost(request):
    pk = request.data.get("pk")
    if not pk:
        return Response({"error": "Missing 'pk' field"}, status=400)

    post = Post.objects.get(pk=pk)

    # Get both variants
    variant_a = ContentVariant.objects.filter(variant_id="A", post=post).first()
    variant_b = ContentVariant.objects.filter(variant_id="B", post=post).first()

    results = {}

    # Post variant A
    if variant_a:
        text_a = variant_a.content
        media_a = getattr(getattr(variant_a, "asset", None), "name", None)
        resp_a = requests.post(
            "http://localhost:8000/clone/2/tweets",
            headers={"Content-Type": "application/json"},
            json={"text": text_a, "media": media_a}
        )
        if resp_a.status_code == 201:
            tweet_id_a = resp_a.json().get("data", {}).get("id")
            results['A'] = tweet_id_a

    # Post variant B
    if variant_b:
        text_b = variant_b.content
        media_b = getattr(getattr(variant_b, "asset", None), "name", None)
        resp_b = requests.post(
            "http://localhost:8000/clone/2/tweets",
            headers={"Content-Type": "application/json"},
            json={"text": text_b, "media": media_b}
        )
        if resp_b.status_code == 201:
            tweet_id_b = resp_b.json().get("data", {}).get("id")
            results['B'] = tweet_id_b

    # Update PostMetrics with both tweet_ids
    postMetrics = post.metrics
    if postMetrics:
        postMetrics.tweet_id = results  # {"A": "123", "B": "456"}
        postMetrics.save()

    post.status = "published"
    post.save()

    return Response({"success": True, "tweet_ids": results}, status=201)
```

### 2.2 Update getXPostMetrics Endpoint
**File**: `backend/src/metrics/views.py:178-222`

**Changes**:
- Fetch metrics for **both** tweet_ids (A and B)
- Store in JSONField format: `{"A": value, "B": value}`

**New Logic**:
```python
@api_view(['POST'])
def getXPostMetrics(request):
    pk = request.data.get("pk")
    if not pk:
        return Response({"error": "Missing 'pk' field"}, status=400)

    post = Post.objects.get(pk=pk)
    postMetrics = post.metrics
    tweet_ids = postMetrics.tweet_id  # {"A": "123", "B": "456"}

    metrics_data = {"A": {}, "B": {}}

    # Fetch metrics for variant A
    if tweet_ids.get("A"):
        resp_a = requests.post(
            "http://localhost:8000/clone/2/metrics/",
            headers={"Content-Type": "application/json"},
            json={"tweet_ids": tweet_ids["A"]}
        )
        if resp_a.status_code == 200:
            data_a = resp_a.json().get("data", [])[0]
            pub_a = data_a.get("public_metrics", {})
            nonpub_a = data_a.get("non_public_metrics", {})
            comments_a = CloneComment.objects.filter(
                tweet__tweet_id=tweet_ids["A"]
            ).values_list('text', flat=True)

            metrics_data["A"] = {
                "likes": pub_a.get("like_count", 0),
                "retweets": pub_a.get("retweet_count", 0),
                "comments": pub_a.get("reply_count", 0),
                "impressions": nonpub_a.get("impression_count", 0),
                "commentList": list(comments_a)
            }

    # Fetch metrics for variant B (same logic)
    if tweet_ids.get("B"):
        # ... similar code for variant B

    # Update PostMetrics with A/B structure
    postMetrics.likes = {
        "A": metrics_data["A"].get("likes", 0),
        "B": metrics_data["B"].get("likes", 0)
    }
    postMetrics.retweets = {
        "A": metrics_data["A"].get("retweets", 0),
        "B": metrics_data["B"].get("retweets", 0)
    }
    postMetrics.comments = {
        "A": metrics_data["A"].get("comments", 0),
        "B": metrics_data["B"].get("comments", 0)
    }
    postMetrics.impressions = {
        "A": metrics_data["A"].get("impressions", 0),
        "B": metrics_data["B"].get("impressions", 0)
    }
    postMetrics.commentList = {
        "A": metrics_data["A"].get("commentList", []),
        "B": metrics_data["B"].get("commentList", [])
    }
    postMetrics.save()

    return Response({"success": True, "metrics": metrics_data}, status=200)
```

### 2.3 Update nodesJSON Endpoint
**File**: `backend/src/metrics/views.py:82-135`

**Changes**:
- Return metrics in new A/B structure
- Use `get_max_metrics()` for backward compatibility

**New Response Format**:
```python
def getMetricsDB():
    posts = Post.objects.filter(status="published").select_related('metrics')
    out = {}
    for post in posts:
        m = getattr(post, "metrics", None)
        if m:
            out[int(post.pk)] = {
                "A": {
                    "likes": m.likes.get("A", 0),
                    "retweets": m.retweets.get("A", 0),
                    "comments": m.comments.get("A", 0),
                    "impressions": m.impressions.get("A", 0),
                },
                "B": {
                    "likes": m.likes.get("B", 0),
                    "retweets": m.retweets.get("B", 0),
                    "comments": m.comments.get("B", 0),
                    "impressions": m.impressions.get("B", 0),
                }
            }
    return out

# In nodesJSON view, also update post_metrics to aggregate A+B
post_metrics = []
for post in chartPosts:
    m = getattr(post, "metrics", None)
    if m:
        agg = m.get_aggregated_metrics()
        post_metrics.append({
            "pk": post.pk,
            "title": post.title,
            "description": post.description,
            "likes": agg['likes'],
            "retweets": agg['retweets'],
            "impressions": agg['impressions'],
            "comments": agg['comments'],
        })
```

### 2.4 Update approveAllNodes Endpoint
**File**: `backend/src/metrics/views.py:328-412`

**Changes**:
- Post both variants A and B for each approved post
- Similar to createXPost changes

---

## Phase 3: Frontend Type Updates

### 3.1 Update TypeScript Interfaces
**File**: `frontend/janus/src/types/api.ts`

**Changes**:
```typescript
// New variant metrics structure
export interface VariantMetrics {
  likes: number;
  retweets: number;
  comments: number;
  impressions: number;
}

// Updated NodeMetrics to support A/B
export interface NodeMetrics {
  A: VariantMetrics;
  B: VariantMetrics;
}

// PostMetrics stays the same for chart view (already aggregated)
export interface PostMetrics {
  pk: number;
  title: string;
  description: string;
  likes: number;      // Aggregated A + B
  retweets: number;   // Aggregated A + B
  impressions: number; // Aggregated A + B
  comments: number;    // Aggregated A + B
}

// Add variant-specific metrics for NodeVariantModal
export interface VariantWithMetrics extends Variant {
  metrics?: VariantMetrics;
}
```

---

## Phase 4: Frontend API Service Updates

### 4.1 Update API Calls
**File**: `frontend/janus/src/services/api.ts`

**No changes needed** - API calls stay the same, only response format changes

---

## Phase 5: Frontend Component Updates

### 5.1 Update Graph Parser
**File**: `frontend/janus/src/utils/graphParser.ts:86-116`

**Changes**:
```typescript
function createReactFlowNode(
  diagramNode: DiagramNode,
  x: number,
  y: number,
  index: number,
  metricsMap: Record<number, NodeMetrics>
): Node {
  // ... existing code ...

  // Get metrics for this node if available
  const metrics = metricsMap[diagramNode.pk];

  // Use MAX metrics for canvas display
  const likes = metrics
    ? Math.max(metrics.A?.likes ?? 0, metrics.B?.likes ?? 0)
    : 1;
  const comments = metrics
    ? Math.max(metrics.A?.retweets ?? 0, metrics.B?.retweets ?? 0)
    : 0;

  // ... rest of code ...
}
```

### 5.2 Update NodeVariantModal
**File**: `frontend/janus/src/components/NodeVariantModal.tsx`

**Changes**:
- Pass actual variant metrics instead of mock data
- Update props to accept metrics per variant

**New Props**:
```typescript
interface NodeVariantModalProps {
  isOpen: boolean;
  onClose: () => void;
  variant1: Variant;
  variant2: Variant;
  variant1Metrics?: VariantMetrics;  // NEW
  variant2Metrics?: VariantMetrics;  // NEW
  onSelectVariant?: (variantNumber: 1 | 2) => void;
}
```

### 5.3 Update CanvasWithPolling
**File**: `frontend/janus/src/components/CanvasWithPolling.tsx:206-224`

**Changes**:
- Fetch variant-specific metrics when opening modal
- Pass to NodeVariantModal

**New Logic**:
```typescript
const handleNodeClick = useCallback(async (node: FlowNode, event?: MouseEvent) => {
  // ... shift-click logic stays same ...

  try {
    const data = await fetchVariants(node.id);

    if (data.variants && data.variants.length >= 2) {
      // Fetch metrics for this node
      const nodeMetrics = metricsMap[parseInt(node.id)]; // From polling data

      setVariants(data.variants);
      setVariantMetrics({
        A: nodeMetrics?.A || { likes: 0, retweets: 0, comments: 0, impressions: 0 },
        B: nodeMetrics?.B || { likes: 0, retweets: 0, comments: 0, impressions: 0 }
      });
      setSelectedNode(node);
    }
  } catch (error) {
    console.error('Failed to fetch variants:', error);
  }
}, []);
```

### 5.4 Update VariantMetricsBox
**File**: `frontend/janus/src/components/VariantMetricsBox.tsx`

**Already complete** - just needs real data passed instead of mock

### 5.5 Update PostMetricsBox
**File**: `frontend/janus/src/components/PostMetricsBox.tsx`

**No changes needed** - already receives aggregated metrics from backend

### 5.6 Update TaskCardNode
**File**: `frontend/janus/src/components/TaskCardNode.tsx`

**No changes needed** - already receives max metrics from graph parser

---

## Phase 6: Data Migration

### 6.1 Create Migration Script
**File**: `backend/src/metrics/migrations/0011_ab_metrics_structure.py`

```python
from django.db import migrations

def migrate_to_ab_structure(apps, schema_editor):
    PostMetrics = apps.get_model('metrics', 'PostMetrics')

    for metric in PostMetrics.objects.all():
        # Convert old single values to A/B structure
        metric.likes = {"A": metric.likes if isinstance(metric.likes, int) else 0, "B": 0}
        metric.retweets = {"A": metric.retweets if isinstance(metric.retweets, int) else 0, "B": 0}
        metric.impressions = {"A": metric.impressions if isinstance(metric.impressions, int) else 0, "B": 0}
        metric.comments = {"A": metric.comments if isinstance(metric.comments, int) else 0, "B": 0}

        # Convert tweet_id
        old_tweet_id = metric.tweet_id if isinstance(metric.tweet_id, str) else ""
        metric.tweet_id = {"A": old_tweet_id, "B": ""}

        # Convert commentList
        old_comments = metric.commentList if isinstance(metric.commentList, list) else []
        metric.commentList = {"A": old_comments, "B": []}

        metric.save()

class Migration(migrations.Migration):
    dependencies = [
        ('metrics', '0010_alter_postmetrics_tweet_id'),
    ]

    operations = [
        # Change field types
        migrations.AlterField(
            model_name='postmetrics',
            name='likes',
            field=models.JSONField(default=dict),
        ),
        # ... repeat for all fields ...

        # Run data migration
        migrations.RunPython(migrate_to_ab_structure),
    ]
```

---

## Testing Plan

### Backend Testing
1. Create new post → both variants posted → both have tweet_ids
2. Fetch metrics → both variants have separate metrics
3. Old posts → variant A has data, variant B is empty
4. nodesJSON endpoint → returns A/B structure
5. Aggregation functions work correctly

### Frontend Testing
1. Canvas nodes show max metrics
2. Chart view shows aggregated metrics
3. NodeVariantModal shows separate A/B metrics
4. Polling updates work correctly
5. Diff detection catches A/B metric changes

---

## Files to Modify Summary

### Backend (7 files)
1. `backend/src/metrics/models.py` - PostMetrics model
2. `backend/src/metrics/views.py` - createXPost, getXPostMetrics, nodesJSON, approveAllNodes
3. `backend/src/metrics/serializer.py` - if needed for serialization
4. `backend/src/metrics/migrations/0011_ab_metrics_structure.py` - NEW migration file
5. `backend/src/metrics/admin.py` - update admin display if needed

### Frontend (6 files)
1. `frontend/janus/src/types/api.ts` - TypeScript interfaces
2. `frontend/janus/src/utils/graphParser.ts` - max metrics logic
3. `frontend/janus/src/utils/graphDiff.ts` - potentially update diff logic
4. `frontend/janus/src/components/NodeVariantModal.tsx` - accept real metrics
5. `frontend/janus/src/components/CanvasWithPolling.tsx` - pass metrics to modal
6. `frontend/janus/src/hooks/useGraphData.ts` - potentially update types

---

## Implementation Order

1. **Backend Model** (models.py) - Core data structure
2. **Migration** - Convert existing data
3. **Backend APIs** (views.py) - Update all endpoints
4. **Frontend Types** (api.ts) - TypeScript definitions
5. **Frontend Parser** (graphParser.ts) - Max metrics logic
6. **Frontend Components** - Display updates
7. **Testing** - End-to-end verification

---

## Risks & Considerations

1. **Data Loss**: Migration must preserve existing metrics as variant A
2. **Breaking Changes**: Frontend must handle both old and new format during transition
3. **Performance**: JSONField queries might be slower than integer fields
4. **Backward Compatibility**: Need fallback logic if variant B doesn't exist

---

## Estimated Effort
- Backend changes: ~4-6 hours
- Frontend changes: ~2-3 hours
- Testing & debugging: ~2-3 hours
- **Total**: ~8-12 hours

---

## Next Steps
After approval of this plan:
1. Create feature branch: `feature/ab-metrics-architecture`
2. Implement backend changes first
3. Test backend thoroughly
4. Implement frontend changes
5. End-to-end testing
6. Code review & merge
