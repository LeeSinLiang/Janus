import { Node, Edge } from '@xyflow/react';

export interface GraphDiff {
  nodesToAdd: Node[];
  nodesToUpdate: Node[];
  nodesToRemove: string[];
  edgesToAdd: Edge[];
  edgesToRemove: string[];
  hasChanges: boolean;
}

/**
 * Compare two graph states and return the differences
 *
 * @param oldNodes - Current nodes in the graph
 * @param oldEdges - Current edges in the graph
 * @param newNodes - New nodes from backend
 * @param newEdges - New edges from backend
 * @returns GraphDiff object with all changes
 */
export function diffGraphData(
  oldNodes: Node[],
  oldEdges: Edge[],
  newNodes: Node[],
  newEdges: Edge[]
): GraphDiff {
  // Create maps for efficient lookup
  const oldNodeMap = new Map(oldNodes.map(node => [node.id, node]));
  const newNodeMap = new Map(newNodes.map(node => [node.id, node]));
  const oldEdgeMap = new Map(oldEdges.map(edge => [edge.id, edge]));
  const newEdgeMap = new Map(newEdges.map(edge => [edge.id, edge]));

  const nodesToAdd: Node[] = [];
  const nodesToUpdate: Node[] = [];
  const nodesToRemove: string[] = [];
  const edgesToAdd: Edge[] = [];
  const edgesToRemove: string[] = [];

  // Find nodes to add and update
  newNodes.forEach(newNode => {
    const oldNode = oldNodeMap.get(newNode.id);

    if (!oldNode) {
      // Node doesn't exist - add it
      nodesToAdd.push(newNode);
    } else {
      // Node exists - check if data changed
      if (hasNodeDataChanged(oldNode, newNode)) {
        // Preserve the user's position
        const updatedNode = {
          ...newNode,
          position: oldNode.position, // Keep existing position
        };
        nodesToUpdate.push(updatedNode);
      }
    }
  });

  // Find nodes to remove
  oldNodes.forEach(oldNode => {
    if (!newNodeMap.has(oldNode.id)) {
      nodesToRemove.push(oldNode.id);
    }
  });

  // Find edges to add
  newEdges.forEach(newEdge => {
    if (!oldEdgeMap.has(newEdge.id)) {
      edgesToAdd.push(newEdge);
    }
  });

  // Find edges to remove
  oldEdges.forEach(oldEdge => {
    if (!newEdgeMap.has(oldEdge.id)) {
      edgesToRemove.push(oldEdge.id);
    }
  });

  const hasChanges =
    nodesToAdd.length > 0 ||
    nodesToUpdate.length > 0 ||
    nodesToRemove.length > 0 ||
    edgesToAdd.length > 0 ||
    edgesToRemove.length > 0;

  return {
    nodesToAdd,
    nodesToUpdate,
    nodesToRemove,
    edgesToAdd,
    edgesToRemove,
    hasChanges,
  };
}

/**
 * Check if node data has changed (title, description, metrics, tags, or assetsReady)
 */
function hasNodeDataChanged(oldNode: Node, newNode: Node): boolean {
  const oldData = oldNode.data as any;
  const newData = newNode.data as any;

  // Compare tags array
  const tagsChanged = !areTagsEqual(oldData?.tags, newData?.tags);

  // Compare relevant fields
  return (
    oldData?.title !== newData?.title ||
    oldData?.description !== newData?.description ||
    oldData?.likes !== newData?.likes ||
    oldData?.comments !== newData?.comments ||
    oldData?.assetsReady !== newData?.assetsReady ||
    tagsChanged
  );
}

/**
 * Compare two tags arrays for equality
 */
function areTagsEqual(oldTags: any[] | undefined, newTags: any[] | undefined): boolean {
  if (!oldTags && !newTags) return true;
  if (!oldTags || !newTags) return false;
  if (oldTags.length !== newTags.length) return false;

  return oldTags.every((oldTag, index) => {
    const newTag = newTags[index];
    return oldTag?.label === newTag?.label && oldTag?.color === newTag?.color;
  });
}

/**
 * Apply diff to existing graph state
 *
 * @param currentNodes - Current nodes array
 * @param currentEdges - Current edges array
 * @param diff - The diff to apply
 * @returns Updated nodes and edges
 */
export function applyGraphDiff(
  currentNodes: Node[],
  currentEdges: Edge[],
  diff: GraphDiff
): { nodes: Node[]; edges: Edge[] } {
  if (!diff.hasChanges) {
    return { nodes: currentNodes, edges: currentEdges };
  }

  // Apply node changes
  let updatedNodes = [...currentNodes];

  // Remove nodes
  if (diff.nodesToRemove.length > 0) {
    updatedNodes = updatedNodes.filter(
      node => !diff.nodesToRemove.includes(node.id)
    );
  }

  // Update existing nodes
  if (diff.nodesToUpdate.length > 0) {
    const updateMap = new Map(diff.nodesToUpdate.map(node => [node.id, node]));
    updatedNodes = updatedNodes.map(node => {
      const update = updateMap.get(node.id);
      return update || node;
    });
  }

  // Add new nodes
  if (diff.nodesToAdd.length > 0) {
    // Position new nodes intelligently
    const positionedNewNodes = positionNewNodes(updatedNodes, diff.nodesToAdd);
    updatedNodes = [...updatedNodes, ...positionedNewNodes];
  }

  // Apply edge changes
  let updatedEdges = [...currentEdges];

  // Remove edges
  if (diff.edgesToRemove.length > 0) {
    updatedEdges = updatedEdges.filter(
      edge => !diff.edgesToRemove.includes(edge.id)
    );
  }

  // Add new edges
  if (diff.edgesToAdd.length > 0) {
    updatedEdges = [...updatedEdges, ...diff.edgesToAdd];
  }

  return {
    nodes: updatedNodes,
    edges: updatedEdges,
  };
}

/**
 * Position new nodes intelligently based on existing nodes
 * Also marks them as pending approval
 * Uses strict phase-based column positioning to maintain layout structure
 */
function positionNewNodes(existingNodes: Node[], newNodes: Node[]): Node[] {
  // Define strict X positions matching dagreLayout.ts
  const PHASE_X_POSITIONS = {
    'Phase 1': 50,    // Left column (200 - 150 for centering)
    'Phase 2': 600,   // Middle column (750 - 150 for centering)
    'Phase 3': 1150,  // Right column (1300 - 150 for centering)
  };

  if (existingNodes.length === 0) {
    // No existing nodes, use positions from parser (dagre layout) and mark as pending
    return newNodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        pendingApproval: true, // Mark new nodes for approval
      },
    }));
  }

  // Group existing nodes by phase to understand layout structure
  const nodesByPhase = new Map<string, Node[]>();
  existingNodes.forEach(node => {
    const phase = String(node.data?.phase || 'Phase 1');
    if (!nodesByPhase.has(phase)) {
      nodesByPhase.set(phase, []);
    }
    nodesByPhase.get(phase)!.push(node);
  });

  // Position new nodes based on their phase
  return newNodes.map((node) => {
    const phase = String(node.data?.phase || 'Phase 1');
    const nodesInSamePhase = nodesByPhase.get(phase) || [];

    // Get strict X position for this phase
    const phaseX = PHASE_X_POSITIONS[phase as keyof typeof PHASE_X_POSITIONS] || PHASE_X_POSITIONS['Phase 1'];

    if (nodesInSamePhase.length > 0) {
      // Position below other nodes in the same phase column
      const maxY = Math.max(...nodesInSamePhase.map(n => n.position.y));

      return {
        ...node,
        position: {
          x: phaseX, // Strict phase column position
          y: maxY + 300, // Below existing nodes in same phase
        },
        data: {
          ...node.data,
          pendingApproval: true,
        },
      };
    } else {
      // No nodes in this phase yet, use position from parser (dagre)
      // New node will maintain its layout-calculated position
      return {
        ...node,
        data: {
          ...node.data,
          pendingApproval: true,
        },
      };
    }
  });
}

/**
 * Merge new nodes with existing nodes, preserving positions
 * This is a helper for the initial load case
 */
export function mergeNodesPreservingPositions(
  existingNodes: Node[],
  newNodes: Node[]
): Node[] {
  const existingMap = new Map(existingNodes.map(node => [node.id, node]));

  return newNodes.map(newNode => {
    const existing = existingMap.get(newNode.id);
    if (existing) {
      // Preserve position from existing node
      return {
        ...newNode,
        position: existing.position,
      };
    }
    return newNode;
  });
}
