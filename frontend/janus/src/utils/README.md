# Mermaid Parser

A parser that converts Mermaid-like graph syntax to ReactFlow nodes and edges.

## Usage

```typescript
import { parseMermaidGraph } from '@/utils/mermaidParser';

const mermaidText = `
graph TB
    subgraph "Phase 1"
        NODE1[<title>Instagram post</title><description>Create content</description>]
        NODE2[<title>X post</title><description>Share update</description>]
    end

    NODE1 --> NODE2
`;

const { nodes, edges } = parseMermaidGraph(mermaidText);

// Use nodes and edges in ReactFlow
<ReactFlow nodes={nodes} edges={edges} ... />
```

## Supported Syntax

### Graph Declaration
```
graph TB  // Top to Bottom (currently the direction is automatic)
```

### Subgraphs
```
subgraph "Phase 1"
    NODE1[...]
    NODE2[...]
end
```

### Node Definitions
```
NODE_ID[<title>Node Title</title><description>Node description text</description>]
```

### Edge Definitions

**Directed Edge:**
```
NODE1 --> NODE2
```

**Bidirectional Edge:**
```
NODE1 <--> NODE2
```

## Features

- ✅ Parses node definitions with title and description
- ✅ Parses directed edges (`-->`)
- ✅ Parses bidirectional edges (`<-->`)
- ✅ Handles subgraphs for organized layouts
- ✅ Automatic positioning based on subgraph grouping
- ✅ Assigns icons and colors to nodes automatically
- ✅ Creates TaskCardNode-compatible data structure

## Layout

- Nodes in subgraphs are laid out horizontally within their group
- Each subgraph occupies a separate row
- Spacing is configurable in the parser constants
- Default spacing: 400px horizontal, 300px vertical

## Future Enhancements

- Parse node attributes (tags, icons, colors) from mermaid syntax
- Support different edge styles (dashed, animated)
- Support different node types
- Custom layout algorithms
- Parse graph direction (TB, LR, etc.)
