'use client';

import { useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  addEdge,
  Connection,
  Edge,
  BackgroundVariant,
  OnNodesChange,
  OnEdgesChange,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import TaskCardNode from './TaskCardNode';
import ChatBox from './ChatBox';
import { useGraphData } from '@/hooks/useGraphData';

const nodeTypes = {
  taskCard: TaskCardNode,
};

export default function CanvasWithPolling() {
  // Fetch graph data with automatic polling and diff-based updates
  // The hook now handles all diffing internally and preserves positions
  const { nodes, edges, loading, error, setNodes, setEdges } = useGraphData({
    pollingInterval: 5000,
    useMockData: true, // Set to false when connecting to real backend
  });

  // Approve a pending node
  const handleApproveNode = useCallback(
    (nodeId: string) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === nodeId
            ? {
                ...node,
                data: {
                  ...node.data,
                  pendingApproval: false, // Remove pending state
                },
              }
            : node
        )
      );
    },
    [setNodes]
  );

  // Reject a pending node (remove it and its connected edges)
  const handleRejectNode = useCallback(
    (nodeId: string) => {
      // Remove the node
      setNodes((nds) => nds.filter((node) => node.id !== nodeId));

      // Remove all edges connected to this node
      setEdges((eds) =>
        eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId)
      );
    },
    [setNodes, setEdges]
  );

  // Add handlers to node data
  const nodesWithHandlers = nodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      onApprove: () => handleApproveNode(node.id),
      onReject: () => handleRejectNode(node.id),
    },
  }));

  // Handle node changes (dragging, etc.)
  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    [setNodes]
  );

  // Handle edge changes
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
    },
    [setEdges]
  );

  // Handle connecting new edges
  const onConnect = useCallback(
    (params: Edge | Connection) => {
      const newEdge = {
        ...params,
        type: 'smoothstep',
        style: { stroke: '#94A3B8', strokeWidth: 2 },
      };
      setEdges((eds) => addEdge(newEdge as Edge, eds));
    },
    [setEdges]
  );

  // Show loading state on initial load
  if (loading && nodes.length === 0) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-50">
        <div className="text-zinc-600">Loading graph...</div>
      </div>
    );
  }

  // Show error state if there's an error and no data
  if (error && nodes.length === 0) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-50">
        <div className="text-red-600">Error loading graph: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full bg-gray-50">
      {/* ReactFlow Canvas */}
      <ReactFlow
        nodes={nodesWithHandlers}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Controls />
        <Background color="#e5e7eb" variant={BackgroundVariant.Dots} gap={16} size={4} />
      </ReactFlow>

      {/* Floating ChatBox at the bottom */}
      <div className="pointer-events-none absolute inset-x-0 bottom-8 flex justify-center px-4">
        <div className="pointer-events-auto w-full max-w-[50%] rounded-xl border border-zinc-200 bg-white shadow-lg">
          <ChatBox nodes={nodesWithHandlers} />
        </div>
      </div>
    </div>
  );
}
