'use client';

import { useCallback, useState } from 'react';
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
import ViewToggle from './ViewToggle';
import { useGraphData } from '@/hooks/useGraphData';
import { approveNode, rejectNode } from '@/services/api';

const nodeTypes = {
  taskCard: TaskCardNode,
};

interface RejectionState {
  nodeId: string;
  nodeName: string;
}

export default function CanvasWithPolling() {
  // View state
  const [activeView, setActiveView] = useState<'node-editor' | 'chart'>('node-editor');

  // Rejection flow state
  const [rejectionState, setRejectionState] = useState<RejectionState | null>(null);

  // Fetch graph data with automatic polling and diff-based updates
  // The hook now handles all diffing internally and preserves positions
  const { nodes, edges, loading, error, setNodes, setEdges } = useGraphData({
    pollingInterval: 5000,
    useMockData: true, // Set to false when connecting to real backend
  });

  // Approve a pending node
  const handleApproveNode = useCallback(
    async (nodeId: string) => {
      // Find the node to get its name
      const node = nodes.find(n => n.id === nodeId);
      if (!node) return;

      const nodeName = String(node.data?.title || nodeId);

      try {
        // Send approval to backend
        await approveNode(nodeName);

        // Update UI - remove pending state
        setNodes((nds) =>
          nds.map((node) =>
            node.id === nodeId
              ? {
                  ...node,
                  data: {
                    ...node.data,
                    pendingApproval: false,
                  },
                }
              : node
          )
        );
      } catch (error) {
        console.error('Failed to approve node:', error);
        // Optionally show error to user
      }
    },
    [nodes, setNodes]
  );

  // Initiate rejection flow - set state to trigger ChatBox focus
  const handleRejectNode = useCallback(
    (nodeId: string) => {
      const node = nodes.find(n => n.id === nodeId);
      if (!node) return;

      const nodeName = String(node.data?.title || nodeId);

      // Set rejection state - this will trigger ChatBox to focus
      setRejectionState({ nodeId, nodeName });
    },
    [nodes]
  );

  // Handle rejection submission from ChatBox
  const handleRejectionSubmit = useCallback(
    async (rejectMessage: string) => {
      if (!rejectionState) return;

      try {
        // Send rejection to backend
        await rejectNode(rejectionState.nodeName, rejectMessage);

        // Remove the node from UI
        setNodes((nds) => nds.filter((node) => node.id !== rejectionState.nodeId));

        // Remove all edges connected to this node
        setEdges((eds) =>
          eds.filter((edge) => edge.source !== rejectionState.nodeId && edge.target !== rejectionState.nodeId)
        );

        // Clear rejection state
        setRejectionState(null);
      } catch (error) {
        console.error('Failed to reject node:', error);
        // Optionally show error to user
      }
    },
    [rejectionState, setNodes, setEdges]
  );

  // Cancel rejection flow
  const handleCancelRejection = useCallback(() => {
    setRejectionState(null);
  }, []);

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
        type: 'default',
        markerEnd: 'arrow',
         animated: true,
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
      {/* View Toggle - positioned at top left */}
      <div className="absolute left-8 top-8 z-10">
        <ViewToggle activeView={activeView} onViewChange={setActiveView} />
      </div>

      {/* Conditional view rendering */}
      {activeView === 'node-editor' ? (
        <>
          {/* ReactFlow Canvas */}
          <ReactFlow
            nodes={nodesWithHandlers}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: {left: 0.3, top: 0.3, right: 0.3, bottom: 1.5} }}
          >
            <Controls />
            <Background color="#e5e7eb" variant={BackgroundVariant.Dots} gap={16} size={4} />
          </ReactFlow>

          {/* Floating ChatBox at the bottom */}
          <div className="pointer-events-none absolute inset-x-0 bottom-8 flex justify-center px-4">
            <div className="pointer-events-auto w-full max-w-[50%] rounded-xl border border-zinc-200 bg-white shadow-lg">
              <ChatBox
                nodes={nodesWithHandlers}
                rejectionState={rejectionState}
                onRejectionSubmit={handleRejectionSubmit}
                onCancelRejection={handleCancelRejection}
              />
            </div>
          </div>
        </>
      ) : (
        /* Chart View Placeholder */
        <div className="flex h-full w-full items-center justify-center">
          <div className="text-center">
            <svg
              width="80"
              height="80"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mx-auto mb-4 text-gray-300"
            >
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-700">Chart View</h2>
            <p className="mt-2 text-gray-500">Coming soon...</p>
          </div>
        </div>
      )}
    </div>
  );
}
