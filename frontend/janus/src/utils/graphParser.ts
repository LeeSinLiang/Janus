import { Node, Edge, MarkerType } from '@xyflow/react';
import { DiagramNode, NodeMetrics } from '@/types/api';
import { applyDagreLayout } from './dagreLayout';

interface ParseResult {
  nodes: Node[];
  edges: Edge[];
}

// Available attribute tags
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
 * Parse JSON diagram data and convert to ReactFlow nodes and edges
 * Applies automatic dagre layout for phase-aware hierarchical positioning
 *
 * @param diagramNodes - Array of diagram nodes from backend
 * @param metrics - Optional object of metrics keyed by post pk
 * @returns Positioned nodes and edges ready for ReactFlow
 */
export function parseGraphData(
  diagramNodes: DiagramNode[],
  metrics?: Record<number, NodeMetrics>
): ParseResult {
  // Convert diagram nodes to ReactFlow nodes (with temporary positions)
  const reactFlowNodes = convertNodesToReactFlow(diagramNodes, metrics || {});

  // Convert next_posts relationships to edges
  const reactFlowEdges = convertEdgesToReactFlow(diagramNodes);

  // Apply dagre layout for hierarchical, phase-aware positioning
  // This minimizes edge crossings and organizes by phase
  const layoutedNodes = applyDagreLayout(reactFlowNodes, reactFlowEdges);

  return {
    nodes: layoutedNodes,
    edges: reactFlowEdges,
  };
}

/**
 * Convert diagram nodes to ReactFlow node format with automatic positioning
 */
function convertNodesToReactFlow(
  diagramNodes: DiagramNode[],
  metricsMap: Record<number, NodeMetrics>
): Node[] {
  const nodes: Node[] = [];

  // Layout configuration
  const HORIZONTAL_SPACING = 400;
  const VERTICAL_SPACING = 300;
  const NODES_PER_ROW = 3;

  diagramNodes.forEach((diagramNode, index) => {
    const row = Math.floor(index / NODES_PER_ROW);
    const col = index % NODES_PER_ROW;
    const x = 50 + (col * HORIZONTAL_SPACING);
    const y = 50 + (row * VERTICAL_SPACING);

    nodes.push(createReactFlowNode(diagramNode, x, y, index, metricsMap));
  });

  return nodes;
}

/**
 * Create a single ReactFlow node from diagram node data
 */
function createReactFlowNode(
  diagramNode: DiagramNode,
  x: number,
  y: number,
  index: number,
  metricsMap: Record<number, NodeMetrics>
): Node {
  // Assign icon and color based on index (cycling through available options)
  const icon = DEFAULT_ICONS[index % DEFAULT_ICONS.length];
  const iconBg = DEFAULT_COLORS[index % DEFAULT_COLORS.length];

  // Determine tags based on post status
  const statusTag = diagramNode.status === 'published'
    ? { label: 'Published', color: '#10B981' }  // Green for published
    : ATTRIBUTES.PLANNED;  // Yellow for draft/planned

  const tags = [statusTag];

  // Add a clock emoji tag if the node has a trigger
  if (diagramNode.has_trigger) {
    tags.push({ label: '⏰', color: '#A1A1AA' }); // A neutral gray color
  }

  // Get metrics for this node if available
  const metrics = metricsMap[diagramNode.pk];
  const likes = metrics?.likes ?? 1;
  const comments = metrics?.retweets ?? 0; // Using retweets as comments

  // Check if node is pending approval (status === 'draft')
  const pendingApproval = diagramNode.status === 'draft';

  return {
    id: String(diagramNode.pk),
    type: 'taskCard',
    position: { x, y },
    data: {
      icon,
      iconBg,
      title: diagramNode.title,
      description: diagramNode.description,
      likes,
      comments,
      tags,
      phase: diagramNode.phase, // Include phase for layout algorithm
      pendingApproval, // Flag for showing approve/reject buttons
      assetsReady: diagramNode.assets_ready, // Flag for showing asset loading indicator
    },
  };
}

/**
 * Convert next_posts relationships to ReactFlow edge format
 */
function convertEdgesToReactFlow(diagramNodes: DiagramNode[]): Edge[] {
  const edges: Edge[] = [];

  diagramNodes.forEach((node) => {
    // Create an edge for each connection in next_posts
    node.next_posts.forEach((targetPk) => {
      edges.push({
        id: `e${node.pk}-${targetPk}`, // Stable ID based on source and target
        source: String(node.pk),
        target: String(targetPk),
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
        type: 'default',
        style: { stroke: '#94A3B8', strokeWidth: 2 },
      });
    });
  });

  return edges;
}
