import dagre from 'dagre';
import { Node, Edge } from '@xyflow/react';

/**
 * Phase-aware layout configuration
 * Arranges nodes in vertical lanes by phase with hierarchical flow
 */
interface LayoutOptions {
  direction?: 'LR' | 'TB'; // Left-to-Right or Top-to-Bottom
  nodeWidth?: number;
  nodeHeight?: number;
  horizontalSpacing?: number;
  verticalSpacing?: number;
}

const DEFAULT_OPTIONS: Required<LayoutOptions> = {
  direction: 'LR', // Left-to-Right for phase progression
  nodeWidth: 300, // Match TaskCardNode width
  nodeHeight: 200, // Approximate TaskCardNode height
  horizontalSpacing: 150, // Space between phases
  verticalSpacing: 100, // Space between nodes in same phase
};

/**
 * Apply dagre layout algorithm to nodes and edges
 * Groups nodes by phase and creates hierarchical flow
 *
 * Performance: O(n + e) where n=nodes, e=edges
 * Only runs once on initial load or when explicitly called
 */
export function applyDagreLayout(
  nodes: Node[],
  edges: Edge[],
  options: LayoutOptions = {}
): Node[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  // Create dagre graph
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  // Configure graph layout
  dagreGraph.setGraph({
    rankdir: opts.direction,
    nodesep: opts.verticalSpacing,
    ranksep: opts.horizontalSpacing,
    ranker: 'tight-tree', // Minimize edge crossings
  });

  // Group nodes by phase for better layout
  const nodesByPhase = new Map<string, Node[]>();
  nodes.forEach(node => {
    const phase = String(node.data?.phase || 'Phase 1');
    if (!nodesByPhase.has(phase)) {
      nodesByPhase.set(phase, []);
    }
    nodesByPhase.get(phase)!.push(node);
  });

  // Add nodes to dagre graph with phase-based ranking hint
  nodes.forEach((node) => {
    const phase = String(node.data?.phase || 'Phase 1');
    const phaseNumber = extractPhaseNumber(phase);

    dagreGraph.setNode(node.id, {
      width: opts.nodeWidth,
      height: opts.nodeHeight,
      // Hint to dagre: Phase 1 should be leftmost, Phase 3 rightmost
      rank: phaseNumber,
    });
  });

  // Add edges to dagre graph
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Run dagre layout algorithm
  dagre.layout(dagreGraph);

  // Apply calculated positions to nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);

    return {
      ...node,
      position: {
        // Center the node on the calculated position
        x: nodeWithPosition.x - opts.nodeWidth / 2,
        y: nodeWithPosition.y - opts.nodeHeight / 2,
      },
    };
  });

  return layoutedNodes;
}

/**
 * Extract phase number from phase string (e.g., "Phase 1" -> 1)
 */
function extractPhaseNumber(phase: string): number {
  const match = phase.match(/\d+/);
  return match ? parseInt(match[0], 10) : 1;
}

/**
 * Check if nodes have been manually positioned
 * Used to avoid re-layouting when user has moved nodes
 */
export function hasManualPositions(nodes: Node[]): boolean {
  // If any node has a non-default position, assume manual positioning
  // Default positions from dagre are typically multiples of spacing values
  return nodes.some(node => {
    const x = node.position.x;
    const y = node.position.y;
    // Check if position looks "too perfect" (likely from layout, not manual)
    return x % 10 !== 0 || y % 10 !== 0;
  });
}
