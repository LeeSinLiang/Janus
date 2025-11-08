# Graph Diff System Documentation

## Overview

The graph diff system implements incremental updates to the ReactFlow canvas, only applying changes instead of rebuilding the entire graph. This provides significant performance improvements and preserves user interactions like node positions.

## Benefits

### ✅ **Performance**
- **O(n) complexity** instead of O(n²) for graph updates
- Only processes changed nodes/edges
- Scales well as graph grows to hundreds of nodes

### ✅ **User Experience**
- Preserves user-dragged node positions
- No jarring full reloads
- Smooth, seamless updates
- Maintains zoom and pan state

### ✅ **Efficiency**
- Minimal React re-renders
- Reduced memory allocation
- Lower CPU usage during polling

## How It Works

### 1. **Initial Load**
```
Backend Response → Parse Mermaid → Full Graph Load → Display
```

### 2. **Subsequent Updates**
```
Backend Response → Parse Mermaid → Diff Computation → Apply Changes → Update Display
```

## Architecture

```typescript
// Old approach (replaced)
Backend data → Parse → Replace entire graph

// New approach (current)
Backend data → Parse → Compute diff → Apply only changes
```

## Key Components

### 1. `graphDiff.ts` - Diff Utility

#### `diffGraphData()`
Compares old and new graph states and returns differences.

**Returns:**
```typescript
interface GraphDiff {
  nodesToAdd: Node[];        // New nodes to add
  nodesToUpdate: Node[];     // Existing nodes with changed data
  nodesToRemove: string[];   // Node IDs to remove
  edgesToAdd: Edge[];        // New edges to add
  edgesToRemove: string[];   // Edge IDs to remove
  hasChanges: boolean;       // Whether any changes exist
}
```

#### `applyGraphDiff()`
Applies a computed diff to the current graph state.

**Process:**
1. Remove deleted nodes
2. Update existing nodes (preserving positions)
3. Add new nodes (smart positioning)
4. Remove deleted edges
5. Add new edges

#### `positionNewNodes()`
Intelligently positions new nodes below existing ones.

### 2. `useGraphData.ts` - Hook with Diff

**Updated behavior:**
- **Initial load**: Uses full data from backend
- **Subsequent polls**: Computes and applies diff
- **Position preservation**: Keeps user-dragged positions
- **Data updates**: Updates node content when title/description changes

### 3. `CanvasWithPolling.tsx` - Component

Now uses direct node/edge state from hook with proper change handlers for user interactions.

## What Gets Updated

### ✅ **Nodes**

**Added when:**
- New node appears in backend response
- Positioned below existing nodes

**Updated when:**
- `title` changes
- `description` changes
- `likes` (metrics) change
- `comments` (retweets) change

**Removed when:**
- Node no longer in backend response

**Position preserved:**
- User drags a node
- Backend sends update with same node ID
- Position from user drag is kept

### ✅ **Edges**

**Added when:**
- New edge appears in backend response

**Removed when:**
- Edge no longer in backend response

**Note:** Edges cannot be updated, only added/removed per requirements.

## Example Scenarios

### Scenario 1: New Node Added

**Backend sends:**
```json
{
  "diagram": "... NODE6[<title>New Task</title>...] ...",
  "changes": true
}
```

**Result:**
- Diff finds 1 node to add
- New node positioned below existing nodes
- Existing nodes unchanged
- Existing node positions preserved

### Scenario 2: Node Data Updated

**Backend sends updated metrics:**
```json
{
  "metrics": [
    { "node_id": "NODE1", "likes": 150 }  // was 124
  ],
  "changes": true
}
```

**Result:**
- Diff finds 1 node to update
- NODE1's likes updated to 150
- NODE1's position preserved
- All other nodes unchanged

### Scenario 3: Node Removed

**Backend removes NODE3:**
```json
{
  "diagram": "... (NODE3 not included) ...",
  "changes": true
}
```

**Result:**
- Diff finds 1 node to remove
- NODE3 removed from canvas
- Edges connected to NODE3 removed
- Other nodes unchanged

### Scenario 4: User Drags Node

**User action:**
- Drags NODE2 to position (300, 400)

**Next backend update:**
```json
{
  "changes": true,
  // NODE2 still in response
}
```

**Result:**
- Diff finds NODE2 exists
- Position (300, 400) from user drag is preserved
- NODE2's data updated if changed
- Auto-layout position ignored

## Performance Comparison

### Old System (Full Rebuild)
```
5 nodes → 5 operations
50 nodes → 50 operations
500 nodes → 500 operations
```

### New System (Diff-Based)
```
5 nodes, 1 new → 1 operation
50 nodes, 2 updated → 2 operations
500 nodes, 3 changed → 3 operations
```

**Improvement:** O(n) → O(changes)

## Console Logging

The system provides detailed logging for debugging:

```
Initial load, building graph...
Loaded 5 nodes and 8 edges

Changes detected, computing diff...
Diff summary: {
  nodesToAdd: 1,
  nodesToUpdate: 2,
  nodesToRemove: 0,
  edgesToAdd: 2,
  edgesToRemove: 1
}

No changes detected, keeping existing graph
```

## Testing the Diff System

### Test Case 1: Add Node

Update mock data in `api.ts`:
```typescript
// Add NODE6 to diagram
diagram: `... NODE6[<title>New</title>...] ...`
changes: true
```

### Test Case 2: Update Metrics

Update mock data:
```typescript
metrics: [
  { node_id: 'NODE1', likes: 999 }  // Changed
]
changes: true
```

### Test Case 3: Remove Node

Update mock data:
```typescript
// Remove NODE5 from diagram
changes: true
```

### Test Case 4: Position Preservation

1. Start app
2. Drag a node to new position
3. Wait 5+ seconds for next poll
4. Verify node stays at dragged position

## Configuration

No configuration needed - diff system is automatic.

To disable (for debugging):
- Revert to Canvas.tsx instead of CanvasWithPolling.tsx

## Troubleshooting

### Issue: Positions not preserved

**Cause:** Node ID mismatch between backend and frontend

**Fix:** Ensure backend NODE_ID matches exactly:
```
Backend: NODE1
Frontend: NODE1  ✅
Frontend: node1  ❌ (case mismatch)
```

### Issue: Nodes not updating

**Cause:** `changes: false` in backend response

**Fix:** Backend should set `changes: true` when data changes

### Issue: Duplicate nodes

**Cause:** Node ID collision

**Fix:** Ensure unique node IDs in backend diagram

## Future Enhancements

- [ ] Animate node additions/removals
- [ ] Batch multiple rapid changes
- [ ] Optimistic updates (show changes before backend confirms)
- [ ] Undo/redo support
- [ ] Conflict resolution for simultaneous edits
- [ ] Graph diff visualization (show what changed)
