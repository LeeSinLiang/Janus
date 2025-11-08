# Graph Polling System Documentation

## Overview

The graph polling system automatically fetches data from the Django backend every 5 seconds and rebuilds the ReactFlow canvas when changes are detected.

## Architecture

```
Django Backend (REST API)
    ↓
API Service (fetchGraphData)
    ↓
useGraphData Hook (5s polling)
    ↓
Mermaid Parser (parseMermaidGraph)
    ↓
Canvas Component (ReactFlow)
```

## Key Components

### 1. API Types (`/src/types/api.ts`)
TypeScript interfaces matching the backend JSON response:
- `GraphResponse`: Main response structure
- `NodeMetrics`: Metrics for individual nodes
- `ApiError`: Error handling

### 2. API Service (`/src/services/api.ts`)
- `fetchGraphData()`: Fetches from real backend
- `fetchGraphDataMock()`: Mock data for development

### 3. Mermaid Parser (`/src/utils/mermaidParser.ts`)
- Parses Mermaid-like graph syntax
- Applies metrics to nodes
- Generates ReactFlow-compatible nodes and edges

### 4. useGraphData Hook (`/src/hooks/useGraphData.ts`)
- Polls backend every 5 seconds
- Only rebuilds graph when `changes: true`
- Provides loading and error states
- Automatic cleanup on unmount

### 5. Canvas Components
- `Canvas.tsx`: Original static canvas (kept for reference)
- `CanvasWithPolling.tsx`: New polling-enabled canvas

## Backend Response Format

The backend should return JSON matching this structure:

```json
{
  "diagram": "graph TB\n    subgraph \"Phase 1\"\n        NODE1[<title>Title</title><description>Description</description>]\n    end\n    NODE1 --> NODE2",
  "metrics": [
    {
      "node_id": "NODE1",
      "likes": 124,
      "impressions": 1570,
      "retweets": 45
    }
  ],
  "changes": false
}
```

### Fields:
- **diagram**: Mermaid graph text with embedded XML-style tags for node data
- **metrics**: Array of metrics keyed by `node_id` (must match NODE_ID in diagram)
- **changes**: Boolean indicating whether frontend should rebuild the graph

## How Polling Works

1. **Initial Load**: Hook fetches data immediately on mount
2. **Polling Loop**: Fetches data every 5 seconds
3. **Change Detection**: If `changes: true`, graph is rebuilt
4. **No Changes**: If `changes: false`, keeps existing graph (saves performance)
5. **Cleanup**: Interval is cleared when component unmounts

## Usage

### In page.tsx:

```typescript
import CanvasWithPolling from '@/components/CanvasWithPolling';

export default function Home() {
  return (
    <div className="h-screen w-screen">
      <CanvasWithPolling />
    </div>
  );
}
```

### Configuration:

```typescript
// In CanvasWithPolling.tsx
const { nodes, edges, loading, error } = useGraphData({
  pollingInterval: 5000,    // Poll every 5 seconds
  useMockData: true,        // Use mock data (set to false for production)
});
```

## Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This sets the Django backend URL for the API service.

## Switching Between Mock and Real Data

### Development (Mock Data):
```typescript
const { nodes, edges } = useGraphData({
  useMockData: true,  // Uses fetchGraphDataMock()
});
```

### Production (Real Backend):
```typescript
const { nodes, edges } = useGraphData({
  useMockData: false,  // Uses fetchGraphData()
});
```

## Metrics Mapping

The parser maps backend metrics to node data:
- `metrics.likes` → `node.data.likes` (displayed as 👍)
- `metrics.retweets` → `node.data.comments` (displayed as 💬)
- `metrics.impressions` → Not currently displayed (available for future use)

## Node ID Matching

**Critical**: The `node_id` in metrics must match the `NODE_ID` used in the mermaid diagram.

Example:
```
Diagram: NODE1[<title>Instagram post</title>...]
Metrics: { "node_id": "NODE1", "likes": 124 }
```

## Performance Considerations

### Change Detection
The backend `changes` field is crucial for performance:
- `changes: false` → No graph rebuild, saves computation
- `changes: true` → Full graph rebuild with new data

### Polling Interval
- Default: 5000ms (5 seconds)
- Adjust based on backend performance and data update frequency
- Lower = more responsive, higher server load
- Higher = less responsive, lower server load

## Error Handling

The hook provides comprehensive error handling:
```typescript
const { nodes, edges, loading, error, refetch } = useGraphData();

if (error) {
  console.error('Graph data error:', error.message);
  // Show error UI or retry
  refetch(); // Manual retry
}
```

## Testing

### Test with Mock Data:
1. Set `useMockData: true`
2. Modify `fetchGraphDataMock()` in `api.ts` to test different scenarios
3. Toggle `changes` field to test rebuild logic

### Test with Real Backend:
1. Ensure Django backend is running
2. Set correct `NEXT_PUBLIC_API_URL`
3. Set `useMockData: false`
4. Monitor browser console for polling logs

## Future Enhancements

- [ ] WebSocket support for real-time updates (instead of polling)
- [ ] Optimistic updates for better UX
- [ ] Graph diff algorithm (update only changed nodes)
- [ ] Retry logic with exponential backoff
- [ ] Authentication token handling
- [ ] Request cancellation on unmount
- [ ] Metrics dashboard
