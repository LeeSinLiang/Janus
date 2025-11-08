# Backend JSON Format

The frontend now expects a pure JSON format for the graph diagram instead of Mermaid syntax.

## Expected Response Structure

```json
{
  "diagram": [
    {
      "pk": 1,
      "title": "Instagram post",
      "description": "Create an Instagram carousel post (5 slides) highlighting our top features.",
      "next_post": [2, 3]
    },
    {
      "pk": 2,
      "title": "X post",
      "description": "Share highlights on X.",
      "next_post": [4]
    }
  ],
  "metrics": [
    {
      "pk": "1",
      "likes": 124,
      "impressions": 1570,
      "retweets": 45
    },
    {
      "pk": "2",
      "likes": 98,
      "impressions": 2034,
      "retweets": 67
    }
  ],
  "changes": false
}
```

## Field Descriptions

### `diagram` (array of nodes)

Each node in the diagram array represents a marketing post/task:

- **`pk`** (number): Primary key / unique identifier for the node
- **`title`** (string): Display title for the node
- **`description`** (string): Detailed description of the marketing task
- **`next_post`** (array of numbers): Array of `pk` values representing which nodes this node connects to

### `metrics` (array)

Metrics are updated every polling cycle (every 5 seconds):

- **`pk`** (string): Primary key matching the diagram node's `pk`
- **`likes`** (number): Number of likes
- **`impressions`** (number): Number of impressions
- **`retweets`** (number): Number of retweets (displayed as "comments" in UI)

### `changes` (boolean)

- **`true`**: Rebuild the graph using the diff algorithm (new nodes added/removed)
- **`false`**: Only update metrics, don't rebuild graph structure

## Important Notes

1. **Node IDs**: Use `pk` (primary key) consistently as integer for nodes, string for metrics
2. **Edges**: Defined by `next_post` array in each node
3. **Polling**: Frontend polls every 5 seconds
4. **Metrics Updates**: Metrics update every cycle regardless of `changes` flag
5. **Graph Rebuild**: Only rebuild graph structure when `changes: true`

## Example Full Response

See `/sample_response.json` for a complete working example.
