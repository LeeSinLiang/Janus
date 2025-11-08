# Node Approval System Documentation

## Overview

The approval system allows users to review and accept/reject new nodes that are added to the graph via backend updates. New nodes appear with a green border and approve/reject buttons, giving users control over what gets added to their workflow.

## Features

### ✅ Visual Indicators
- **Green border**: New pending nodes have a thick green border (`border-4 border-green-400`)
- **Green background**: Subtle green background (`bg-green-50`) to highlight pending state
- **Approve/Reject buttons**: Positioned above the node in the top-right corner

### ✅ User Actions

**Approve (Green Checkmark)**
- Removes pending state
- Node returns to normal appearance
- Node remains in graph
- All edges stay intact

**Reject (Red X)**
- Removes node from graph
- Removes all connected edges
- Cannot be undone (until backend sends it again)

## How It Works

### 1. **New Node Detection**
When the diff system detects new nodes:
```typescript
// In graphDiff.ts
nodesToAdd.map(node => ({
  ...node,
  data: {
    ...node.data,
    pendingApproval: true  // Mark as pending
  }
}))
```

### 2. **Visual Presentation**
The TaskCardNode component checks for pending status:
```typescript
const isPending = data.pendingApproval || false;

<div className={isPending
  ? 'border-4 border-green-400 bg-green-50'
  : 'border border-zinc-200 bg-white'
}>
```

### 3. **User Decision**

**Approve:**
```typescript
handleApproveNode(nodeId) {
  // Remove pendingApproval flag
  node.data.pendingApproval = false
}
```

**Reject:**
```typescript
handleRejectNode(nodeId) {
  // Remove node from graph
  nodes = nodes.filter(n => n.id !== nodeId)
  // Remove connected edges
  edges = edges.filter(e =>
    e.source !== nodeId && e.target !== nodeId
  )
}
```

## When Nodes Are Marked as Pending

### ✅ **Marked as Pending:**
- New nodes added via diff (after initial load)
- Backend sends `changes: true` with new nodes
- Graph diff detects nodes not in current state

### ❌ **NOT Marked as Pending:**
- Nodes from initial page load
- Nodes with updated data (already approved)
- Nodes manually added by user (future feature)

## UI Components

### Approve Button
```tsx
<button className="bg-green-400 hover:bg-green-500">
  <svg> {/* Checkmark icon */} </svg>
</button>
```
- **Position**: Top-right, above node
- **Size**: 48px × 48px (h-12 w-12)
- **Rounded**: `rounded-xl`
- **Hover**: Scales to 110% and darkens

### Reject Button
```tsx
<button className="bg-red-400 hover:bg-red-500">
  <svg> {/* X icon */} </svg>
</button>
```
- **Position**: Next to approve button
- **Size**: 48px × 48px
- **Rounded**: `rounded-xl`
- **Hover**: Scales to 110% and darkens

## Testing the Approval System

### Method 1: Modify Mock Data

**Step 1**: Initial load with 5 nodes
```typescript
// In api.ts - fetchGraphDataMock()
return {
  diagram: "... 5 nodes ...",
  changes: false
}
```

**Step 2**: After 5+ seconds, add a new node
```typescript
// Update fetchGraphDataMock() to return:
return {
  diagram: "... 6 nodes (add NODE6) ...",
  metrics: [... add NODE6 metrics ...],
  changes: true  // Trigger diff
}
```

**Step 3**: Observe
- NODE6 appears with green border
- Approve/reject buttons appear above NODE6
- Click approve → border turns normal
- Click reject → NODE6 disappears

### Method 2: Use State Toggle

Add a toggle in the component to simulate backend changes:
```typescript
// In api.ts
let includeExtraNode = false;

export function toggleExtraNode() {
  includeExtraNode = !includeExtraNode;
}

export async function fetchGraphDataMock() {
  const baseNodes = "NODE1, NODE2, NODE3, NODE4, NODE5";
  const extraNode = includeExtraNode ? "\nNODE6[<title>New Task</title>...]" : "";

  return {
    diagram: baseNodes + extraNode,
    changes: includeExtraNode,
  };
}
```

### Method 3: Real Backend Testing

Configure backend to send new nodes:
```python
# Django backend
def get_graph(request):
    # Check if new task was created
    if new_tasks_exist():
        diagram = generate_full_diagram()  # Include new nodes
        return {
            "diagram": diagram,
            "metrics": get_metrics(),
            "changes": True  # Trigger approval flow
        }
    else:
        return {
            "changes": False  # No updates
        }
```

## Example Flow

### Scenario: AI suggests new marketing task

1. **Backend generates new node**
   ```
   NODE6[<title>LinkedIn post</title><description>Share article</description>]
   ```

2. **Frontend polls (5s interval)**
   ```
   Backend returns changes: true
   Diff detects NODE6 is new
   ```

3. **NODE6 appears with green border**
   - User sees green highlighted card
   - Approve/reject buttons visible
   - Can still drag and interact with node

4. **User clicks approve ✓**
   - Green border disappears
   - Buttons disappear
   - Node becomes permanent
   - Edges remain connected

5. **OR user clicks reject ✗**
   - Node removed from canvas
   - Connected edges removed
   - Graph re-layouts

## Edge Cases

### What if user drags a pending node?
- ✅ Position is preserved
- ✅ Pending state remains
- ✅ Buttons stay visible
- User can still approve/reject

### What if backend re-sends rejected node?
- ✅ Node reappears as pending
- ✅ User can review again
- This is expected behavior (backend doesn't know it was rejected)

### What if user approves, then backend removes it?
- ✅ Diff will detect removal
- ✅ Node will be removed on next poll
- Approval state is local, backend is source of truth

### What if user doesn't approve/reject?
- Node stays in pending state indefinitely
- User can approve/reject anytime
- Graph functions normally (can drag, connect edges, etc.)

## Customization

### Change approval colors:
```typescript
// In TaskCardNode.tsx
isPending
  ? 'border-4 border-blue-400 bg-blue-50'  // Blue instead of green
  : 'border border-zinc-200 bg-white'
```

### Change button position:
```typescript
<div className="absolute -top-16 right-2">  // Change right-2 to left-2
```

### Add approval timeout:
```typescript
// Auto-approve after 30 seconds
useEffect(() => {
  if (isPending) {
    const timer = setTimeout(() => {
      data.onApprove?.();
    }, 30000);
    return () => clearTimeout(timer);
  }
}, [isPending]);
```

### Show pending count:
```typescript
// In CanvasWithPolling
const pendingCount = nodes.filter(n => n.data.pendingApproval).length;

<div className="absolute top-4 left-4">
  {pendingCount > 0 && (
    <div className="rounded-full bg-green-400 px-3 py-1">
      {pendingCount} pending approval
    </div>
  )}
</div>
```

## Future Enhancements

- [ ] Bulk approve/reject all pending nodes
- [ ] Approval history/undo
- [ ] Reason for rejection (send to backend)
- [ ] Approval required before showing node
- [ ] Email/notification when new nodes pending
- [ ] Approval permissions (admin only)
- [ ] Auto-approve based on rules
- [ ] Preview mode (show but locked until approved)
