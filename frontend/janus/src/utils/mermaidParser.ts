import { Node, Edge } from '@xyflow/react';
import { NodeMetrics } from '@/types/api';

interface ParsedNode {
  id: string;
  title: string;
  description: string;
  subgraph?: string;
}

interface ParsedEdge {
  source: string;
  target: string;
  bidirectional: boolean;
}

interface ParseResult {
  nodes: Node[];
  edges: Edge[];
}

// Available attribute tags (from Canvas.tsx)
const ATTRIBUTES = {
  PLANNED: { label: 'Planned', color: '#FCD34D' },
  FEATURE: { label: 'Feature', color: '#9333EA' },
  FINISHED: { label: 'Finished', color: '#10B981' },
  PROMO: { label: 'Promo', color: '#3B82F6' },
};

// Default icons and colors for nodes
const DEFAULT_ICONS = ['📷', '▶️', '📝', '🎬', '📱', '💻', '🎨', '📊'];
const DEFAULT_COLORS = ['#E4405F', '#FF0000', '#000000', '#3B82F6', '#10B981', '#9333EA'];

/**
 * Parse Mermaid-like graph syntax and convert to ReactFlow nodes and edges
 * @param mermaidText - The mermaid graph text to parse
 * @param metrics - Optional array of metrics to apply to nodes
 */
export function parseMermaidGraph(mermaidText: string, metrics?: NodeMetrics[]): ParseResult {
  const lines = mermaidText.split('\n').map(line => line.trim()).filter(line => line.length > 0);

  const parsedNodes: ParsedNode[] = [];
  const parsedEdges: ParsedEdge[] = [];
  let currentSubgraph: string | undefined = undefined;
  const subgraphs: Map<string, ParsedNode[]> = new Map();

  // Create a map for quick metrics lookup
  const metricsMap = new Map<string, NodeMetrics>();
  if (metrics) {
    metrics.forEach(metric => {
      metricsMap.set(metric.node_id, metric);
    });
  }

  // First pass: Parse nodes and edges
  for (const line of lines) {
    // Skip graph declaration
    if (line.startsWith('graph ')) {
      continue;
    }

    // Handle subgraph start
    const subgraphMatch = line.match(/^subgraph\s+"([^"]+)"/);
    if (subgraphMatch) {
      currentSubgraph = subgraphMatch[1];
      subgraphs.set(currentSubgraph, []);
      continue;
    }

    // Handle subgraph end
    if (line === 'end') {
      currentSubgraph = undefined;
      continue;
    }

    // Parse node definition: NODE1[<title>Title</title><description>Desc</description>]
    const nodeMatch = line.match(/^(\w+)\[<title>([^<]+)<\/title><description>([^<]+)<\/description>\]/);
    if (nodeMatch) {
      const [, id, title, description] = nodeMatch;
      const node: ParsedNode = {
        id,
        title: title.trim(),
        description: description.trim(),
        subgraph: currentSubgraph,
      };
      parsedNodes.push(node);

      if (currentSubgraph && subgraphs.has(currentSubgraph)) {
        subgraphs.get(currentSubgraph)!.push(node);
      }
      continue;
    }

    // Parse bidirectional edge: NODE1 <--> NODE2
    const bidirectionalMatch = line.match(/^(\w+)\s*<-->\s*(\w+)/);
    if (bidirectionalMatch) {
      const [, source, target] = bidirectionalMatch;
      parsedEdges.push({ source, target, bidirectional: true });
      continue;
    }

    // Parse directed edge: NODE1 --> NODE2
    const directedMatch = line.match(/^(\w+)\s*-->\s*(\w+)/);
    if (directedMatch) {
      const [, source, target] = directedMatch;
      parsedEdges.push({ source, target, bidirectional: false });
      continue;
    }
  }

  // Second pass: Convert to ReactFlow format with positioning
  const reactFlowNodes = convertNodesToReactFlow(parsedNodes, subgraphs, metricsMap);
  const reactFlowEdges = convertEdgesToReactFlow(parsedEdges);

  return {
    nodes: reactFlowNodes,
    edges: reactFlowEdges,
  };
}

/**
 * Convert parsed nodes to ReactFlow node format with automatic positioning
 */
function convertNodesToReactFlow(
  parsedNodes: ParsedNode[],
  subgraphs: Map<string, ParsedNode[]>,
  metricsMap: Map<string, NodeMetrics>
): Node[] {
  const nodes: Node[] = [];

  // Layout configuration
  const HORIZONTAL_SPACING = 400;
  const VERTICAL_SPACING = 300;
  const SUBGRAPH_SPACING = 150;

  let currentY = 50;

  // If we have subgraphs, layout by subgraph
  if (subgraphs.size > 0) {
    const subgraphArray = Array.from(subgraphs.entries());

    subgraphArray.forEach(([, subgraphNodes]) => {
      // Layout nodes within this subgraph horizontally
      subgraphNodes.forEach((node, index) => {
        const x = 50 + (index * HORIZONTAL_SPACING);
        const y = currentY;

        nodes.push(createReactFlowNode(node, x, y, index, metricsMap));
      });

      // Move to next row for next subgraph
      currentY += VERTICAL_SPACING + SUBGRAPH_SPACING;
    });

    // Add any nodes not in a subgraph
    const nodesWithoutSubgraph = parsedNodes.filter(n => !n.subgraph);
    nodesWithoutSubgraph.forEach((node, index) => {
      const x = 50 + (index * HORIZONTAL_SPACING);
      const y = currentY;
      nodes.push(createReactFlowNode(node, x, y, index, metricsMap));
    });
  } else {
    // Simple grid layout if no subgraphs
    const NODES_PER_ROW = 3;
    parsedNodes.forEach((node, index) => {
      const row = Math.floor(index / NODES_PER_ROW);
      const col = index % NODES_PER_ROW;
      const x = 50 + (col * HORIZONTAL_SPACING);
      const y = 50 + (row * VERTICAL_SPACING);

      nodes.push(createReactFlowNode(node, x, y, index, metricsMap));
    });
  }

  return nodes;
}

/**
 * Create a single ReactFlow node from parsed node data
 */
function createReactFlowNode(
  parsedNode: ParsedNode,
  x: number,
  y: number,
  index: number,
  metricsMap: Map<string, NodeMetrics>
): Node {
  // Assign icon and color based on index (cycling through available options)
  const icon = DEFAULT_ICONS[index % DEFAULT_ICONS.length];
  const iconBg = DEFAULT_COLORS[index % DEFAULT_COLORS.length];

  // Default tags (can be extended to parse from mermaid text in the future)
  const tags = [ATTRIBUTES.FEATURE, ATTRIBUTES.PLANNED];

  // Get metrics for this node if available
  const metrics = metricsMap.get(parsedNode.id);
  const likes = metrics?.likes ?? 1;
  const comments = metrics?.retweets ?? 0; // Using retweets as comments

  return {
    id: parsedNode.id,
    type: 'taskCard',
    position: { x, y },
    data: {
      icon,
      iconBg,
      title: parsedNode.title,
      description: parsedNode.description,
      likes,
      comments,
      tags,
    },
  };
}

/**
 * Convert parsed edges to ReactFlow edge format
 */
function convertEdgesToReactFlow(parsedEdges: ParsedEdge[]): Edge[] {
  const edges: Edge[] = [];

  parsedEdges.forEach((edge, index) => {
    // For bidirectional edges, create two edges
    if (edge.bidirectional) {
      // Forward edge
      edges.push({
        id: `e${index}-forward`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#94A3B8', strokeWidth: 2 },
      });

      // Backward edge
      edges.push({
        id: `e${index}-backward`,
        source: edge.target,
        target: edge.source,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#94A3B8', strokeWidth: 2, strokeDasharray: '5,5' },
      });
    } else {
      // Single directed edge
      edges.push({
        id: `e${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#94A3B8', strokeWidth: 2 },
      });
    }
  });

  return edges;
}

/**
 * Utility function to read and parse a mermaid file
 */
export async function parseMermaidFile(filePath: string): Promise<ParseResult> {
  const response = await fetch(filePath);
  const text = await response.text();
  return parseMermaidGraph(text);
}
