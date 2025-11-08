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
 * Enforces strict phase-based column positioning
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

  // Define strict X positions for each phase column
  const PHASE_X_POSITIONS = {
    1: 200,   // Phase 1: Left column
    2: 750,   // Phase 2: Middle column
    3: 1300,  // Phase 3: Right column
  };

  // Group nodes by phase for layout
  const nodesByPhase = new Map<number, Node[]>();
  nodes.forEach(node => {
    const phase = String(node.data?.phase || 'Phase 1');
    const phaseNumber = extractPhaseNumber(phase);

    if (!nodesByPhase.has(phaseNumber)) {
      nodesByPhase.set(phaseNumber, []);
    }
    nodesByPhase.get(phaseNumber)!.push(node);
  });

  // Layout each phase column separately using dagre
  const layoutedNodes: Node[] = [];

  [1, 2, 3].forEach(phaseNumber => {
    const phaseNodes = nodesByPhase.get(phaseNumber) || [];
    if (phaseNodes.length === 0) return;

    // Create separate dagre graph for this phase
    const phaseGraph = new dagre.graphlib.Graph();
    phaseGraph.setDefaultEdgeLabel(() => ({}));

    phaseGraph.setGraph({
      rankdir: 'LR', // Left-to-Right for better horizontal distribution
      nodesep: opts.horizontalSpacing / 2, // Horizontal spacing between nodes
      ranksep: opts.verticalSpacing, // Vertical spacing between ranks
    });

    // Add nodes from this phase
    phaseNodes.forEach(node => {
      phaseGraph.setNode(node.id, {
        width: opts.nodeWidth,
        height: opts.nodeHeight,
      });
    });

    // Add edges that connect nodes within this phase
    edges.forEach(edge => {
      const sourceInPhase = phaseNodes.some(n => n.id === edge.source);
      const targetInPhase = phaseNodes.some(n => n.id === edge.target);
      if (sourceInPhase && targetInPhase) {
        phaseGraph.setEdge(edge.source, edge.target);
      }
    });

    // Run dagre layout for this phase
    dagre.layout(phaseGraph);

    // Calculate the centroid X position of all nodes in this phase
    // This helps us center the phase layout around the target X position
    const phaseNodePositions = phaseNodes.map(node => phaseGraph.node(node.id));
    const avgX = phaseNodePositions.reduce((sum, pos) => sum + pos.x, 0) / phaseNodePositions.length;
    const targetPhaseX = PHASE_X_POSITIONS[phaseNumber as keyof typeof PHASE_X_POSITIONS];
    const xOffset = targetPhaseX - avgX;

    // Apply positions - center phase layout around phase column position
    phaseNodes.forEach(node => {
      const nodeWithPosition = phaseGraph.node(node.id);

      layoutedNodes.push({
        ...node,
        position: {
          // Center the dagre layout around the phase column X position
          x: nodeWithPosition.x + xOffset - opts.nodeWidth / 2,
          y: nodeWithPosition.y - opts.nodeHeight / 2,
        },
      });
    });
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
