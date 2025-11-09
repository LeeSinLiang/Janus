# Asset Loading Indicator Feature

## Overview
Visual indicator on draft nodes showing asset generation status, preventing premature approval before images/videos are ready.

## How It Works

### Backend Flow
1. **Post Created** (status='draft')
   - User submits campaign strategy → Posts created
   - `assets_ready = False` (no variants yet)

2. **Background Content Generation Starts**
   - Thread launches: `generate_ab_content_background()`
   - Campaign phase → 'content_creation'

3. **Variants Created**
   - ContentVariant A created (text only) → `assets_ready = False`
   - Image generated for variant A → asset saved
   - ContentVariant B created (text only) → `assets_ready = False`
   - Image generated for variant B → asset saved
   - Both variants complete → `assets_ready = True`

4. **Campaign Ready**
   - Campaign phase → 'scheduled'
   - All posts now have `assets_ready = True`

### Frontend Display

**Draft Nodes (Pending Approval):**
- 🟡 **Yellow pulsing dot** (top-right corner)
  - Means: Assets are still generating in background
  - Tooltip: "Assets loading - please wait..."
  - Approve button: Dimmed (opacity 60%) with wait cursor
  - Action: Wait for green light before approving

- 🟢 **Green solid dot** (top-right corner)
  - Means: Both A/B variants have images/videos ready
  - Tooltip: "Assets ready - safe to approve"
  - Approve button: Normal (full opacity, hover effects)
  - Action: Safe to approve and post

**Published Nodes:**
- No indicator shown (not needed after approval)

### User Experience

#### Scenario 1: Wait for Assets (Recommended)
```
1. Create campaign → Draft nodes appear with 🟡 yellow pulsing light
2. Wait 10-30 seconds (polling every 5s)
3. Light turns 🟢 green → Assets ready!
4. Click approve → Posts with full media
```

#### Scenario 2: Approve Early (Not Recommended)
```
1. Create campaign → Draft nodes appear with 🟡 yellow light
2. Try to click approve immediately
3. Confirmation dialog: "Assets are still loading. Approving now will post without media. Continue?"
4. If YES → Posts without images/videos
5. If NO → Wait for green light
```

## Technical Implementation

### Backend
**File:** `backend/src/metrics/serializer.py`
```python
class PostSerializer(serializers.ModelSerializer):
    assets_ready = serializers.SerializerMethodField()

    def get_assets_ready(self, obj):
        """Check if both variant A and B have assets ready"""
        variant_a = ContentVariant.objects.filter(post=obj, variant_id='A').first()
        variant_b = ContentVariant.objects.filter(post=obj, variant_id='B').first()

        if variant_a and variant_b:
            return bool(variant_a.asset) and bool(variant_b.asset)
        return False
```

**Returns:**
- `false` → Variants missing OR assets not uploaded yet
- `true` → Both variants have assets ready

### Frontend

**Type Definition:** `frontend/janus/src/types/api.ts`
```typescript
export interface DiagramNode {
  pk: number;
  title: string;
  description: string;
  assets_ready?: boolean; // Asset loading status
  // ... other fields
}
```

**Component:** `frontend/janus/src/components/TaskCardNode.tsx`
```tsx
{/* Only show for draft (pending approval) nodes */}
{isPending && assetsReady !== undefined && (
  <div className="absolute -top-2 -right-2 z-20">
    <div className={`h-4 w-4 rounded-full border-2 border-white shadow-md ${
      assetsReady
        ? 'bg-green-500'              // Ready ✓
        : 'bg-yellow-500 animate-pulse' // Loading...
    }`} />
  </div>
)}
```

**Approve Button Protection:**
```tsx
onClick={(e) => {
  e.stopPropagation();

  // Warn if assets not ready
  if (assetsReady === false) {
    if (!confirm('Assets are still loading. Approving now will post without media. Continue?')) {
      return; // User cancelled
    }
  }

  data.onApprove?.(); // Proceed with approval
}}
```

**Data Flow:** `frontend/janus/src/utils/graphParser.ts`
```typescript
return {
  id: String(diagramNode.pk),
  type: 'taskCard',
  data: {
    // ... other fields
    pendingApproval: diagramNode.status === 'draft',
    assetsReady: diagramNode.assets_ready, // Pass through from backend
  },
};
```

## Polling & Updates

**Hook:** `frontend/janus/src/hooks/useGraphData.ts`
- Polls `/nodesJson/` endpoint every **5 seconds**
- Backend returns updated `assets_ready` values
- Frontend re-renders nodes with new status
- Indicator automatically changes from yellow → green

## Asset Generation Timeline

| Time | Event | `assets_ready` | Indicator |
|------|-------|---------------|-----------|
| T+0s | Post created | `false` | 🟡 Yellow pulsing |
| T+5s | Variant A text created | `false` | 🟡 Yellow pulsing |
| T+10s | Variant A image generating... | `false` | 🟡 Yellow pulsing |
| T+15s | Variant A image saved | `false` | 🟡 Yellow pulsing |
| T+20s | Variant B text created | `false` | 🟡 Yellow pulsing |
| T+25s | Variant B image generating... | `false` | 🟡 Yellow pulsing |
| T+30s | Variant B image saved | `true` ✓ | 🟢 Green solid |

**Note:** Actual timing depends on:
- Gemini API response time (content generation: ~2-5s)
- Imagen API response time (image generation: ~5-15s per image)
- Video generation (if enabled): ~30-60s per video

## Files Changed

### Backend
- ✅ `backend/src/metrics/serializer.py` (already existed)
  - Line 13: `assets_ready` field declaration
  - Lines 22-33: Asset checking logic

### Frontend
- ✅ `frontend/janus/src/types/api.ts`
  - Line 13: Added `assets_ready?: boolean` to `DiagramNode`

- ✅ `frontend/janus/src/components/TaskCardNode.tsx`
  - Line 26: Added `assetsReady?: boolean` to `TaskCardData`
  - Lines 43-56: Visual indicator component (top-right corner)
  - Lines 63-79: Approve button warning logic

- ✅ `frontend/janus/src/utils/graphParser.ts`
  - Line 124: Pass `assets_ready` from backend to node data

## Testing

### Manual Test Steps
1. **Start Backend:**
   ```bash
   cd backend/src
   python manage.py runserver
   ```

2. **Start Frontend:**
   ```bash
   cd frontend/janus
   npm run dev
   ```

3. **Create Campaign:**
   - Navigate to http://localhost:3000
   - Enter product description and submit
   - Observe draft nodes appear

4. **Verify Indicators:**
   - ✅ Yellow pulsing dots appear on draft nodes immediately
   - ✅ Approve button is dimmed (opacity 60%)
   - ✅ Hover over indicator shows "Assets loading - please wait..."

5. **Wait for Assets:**
   - Wait 20-40 seconds
   - ✅ Dots turn green solid
   - ✅ Approve button returns to normal opacity
   - ✅ Hover shows "Assets ready - safe to approve"

6. **Test Early Approval (Optional):**
   - Try clicking approve while yellow
   - ✅ Confirmation dialog appears
   - ✅ Can cancel or proceed

7. **Test Normal Approval:**
   - Wait for green light
   - Click approve
   - ✅ Post succeeds with media attached
   - ✅ Indicator disappears (node is now published)

## Troubleshooting

### Indicator Never Turns Green
**Cause:** Background content generation failed or didn't start
**Solution:**
1. Check Django console for errors
2. Verify `GOOGLE_API_KEY` in `.env`
3. Check campaign phase: should be 'scheduled' when complete
4. Query database:
   ```python
   from agents.models import Post, ContentVariant
   post = Post.objects.get(pk=1)
   variants = post.variants.all()
   for v in variants:
       print(f"{v.variant_id}: has asset = {bool(v.asset)}")
   ```

### Indicator Doesn't Appear
**Cause:** Node not in draft status
**Solution:**
- Indicator only shows for `status='draft'`
- Check: `Post.objects.filter(status='draft')`

### All Indicators Stay Yellow
**Cause:** Polling not working or API errors
**Solution:**
1. Check browser console for API errors
2. Test endpoint manually: `curl http://localhost:8000/nodesJson/`
3. Verify `assets_ready` field in response

## Future Enhancements

- [ ] Add progress percentage (e.g., "1/2 variants ready")
- [ ] Show separate status for A vs B variant
- [ ] Add "Refresh Assets" button if generation fails
- [ ] WebSocket support for real-time updates (no polling)
- [ ] Retry logic for failed asset generation
