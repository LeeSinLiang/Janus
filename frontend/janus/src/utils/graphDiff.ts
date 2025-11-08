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
 * Check if node data has changed (title, description, or metrics)
 */
function hasNodeDataChanged(oldNode: Node, newNode: Node): boolean {
  const oldData = oldNode.data;
  const newData = newNode.data;

  // Compare relevant fields
  return (
    oldData?.title !== newData?.title ||
    oldData?.description !== newData?.description ||
    oldData?.likes !== newData?.likes ||
    oldData?.comments !== newData?.comments
  );
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
 */
function positionNewNodes(existingNodes: Node[], newNodes: Node[]): Node[] {
  if (existingNodes.length === 0) {
    // No existing nodes, use positions from parser
    return newNodes;
  }

  // Find the bottom-most node
  const maxY = Math.max(...existingNodes.map(node => node.position.y));
  const VERTICAL_SPACING = 300;
  const HORIZONTAL_SPACING = 400;

  // Position new nodes in a row below existing nodes
  return newNodes.map((node, index) => ({
    ...node,
    position: {
      x: 50 + (index * HORIZONTAL_SPACING),
      y: maxY + VERTICAL_SPACING,
    },
  }));
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
