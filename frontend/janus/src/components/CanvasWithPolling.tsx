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
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import TaskCardNode from './TaskCardNode';
import ChatBox from './ChatBox';
import ViewToggle from './ViewToggle';
import PhaseBar from './PhaseBar';
import NodeVariantModal from './NodeVariantModal';
import WelcomeBar from './WelcomeBar';
import EngagementLineChart from './EngagementLineChart';
import EngagementPieChart from './EngagementPieChart';
import { useGraphData } from '@/hooks/useGraphData';
import { approveNode, rejectNode } from '@/services/api';
import { Node as FlowNode } from '@xyflow/react';

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

  // Modal state for viewing node variants
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null);

  // Phase state
  const [activePhase, setActivePhase] = useState(1); // 0-indexed, so 1 = Phase 2

  // Phase data
  const phases = [
    { name: 'Phase 1', dateRange: '(11 / 01 - 11 / 07)', isActive: activePhase === 0 },
    { name: 'Phase 2', dateRange: '(11 / 08 - 11 / 14)', isActive: activePhase === 1 },
    { name: 'Phase 3', dateRange: '(11 / 15 - 11 / 21)', isActive: activePhase === 2 },
  ];

  // Fetch graph data with automatic polling and diff-based updates
  // The hook now handles all diffing internally and preserves positions
  const { nodes, edges, loading, error, setNodes, setEdges } = useGraphData({
    pollingInterval: 5000,
    useMockData: false, // Set to false when connecting to real backend
  });

  // Approve a pending node
  const handleApproveNode = useCallback(
    async (nodeId: string) => {
      // nodeId is the pk from the backend
      try {
        // Send approval to backend
        await approveNode(nodeId);

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
        // Send rejection to backend (nodeId is the pk)
        await rejectNode(rejectionState.nodeId, rejectMessage);

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

  // Handle node click to show variants
  const handleNodeClick = useCallback((node: FlowNode) => {
    // Only show modal if the node has variants
    if (node.data?.variant1 && node.data?.variant2) {
      setSelectedNode(node);
    }
  }, []);

  // Handle variant selection
  const handleSelectVariant = useCallback((variantNumber: 1 | 2) => {
    if (!selectedNode) return;

    // Update the node with the selected variant
    const selectedVariant = variantNumber === 1
      ? (selectedNode.data.variant1 as { title: string; description: string } | undefined)
      : (selectedNode.data.variant2 as { title: string; description: string } | undefined);

    if (selectedVariant) {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === selectedNode.id
            ? {
                ...node,
                data: {
                  ...node.data,
                  title: selectedVariant.title,
                  description: selectedVariant.description,
                },
              }
            : node
        )
      );
    }

    // Close modal
    setSelectedNode(null);
  }, [selectedNode, setNodes]);

  // Add handlers to node data
  const nodesWithHandlers = nodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      onApprove: () => handleApproveNode(node.id),
      onReject: () => handleRejectNode(node.id),
      onClick: () => handleNodeClick(node),
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
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
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

  // Prepare variant modal data
  const variantModalData = selectedNode && selectedNode.data?.variant1 && selectedNode.data?.variant2 ? {
    variant1: selectedNode.data.variant1 as { title: string; description: string },
    variant2: selectedNode.data.variant2 as { title: string; description: string },
    icon: selectedNode.data.icon as string | undefined,
    iconBg: selectedNode.data.iconBg as string | undefined,
  } : null;

  return (
    <div className="relative h-full w-full bg-gray-50">
      {/* Node Variant Modal */}
      {variantModalData && (
        <NodeVariantModal
          isOpen={!!selectedNode}
          onClose={() => setSelectedNode(null)}
          variant1={{
            title: variantModalData.variant1.title,
            description: variantModalData.variant1.description,
            icon: variantModalData.icon,
            iconBg: variantModalData.iconBg,
          }}
          variant2={{
            title: variantModalData.variant2.title,
            description: variantModalData.variant2.description,
            icon: variantModalData.icon,
            iconBg: variantModalData.iconBg,
          }}
          onSelectVariant={handleSelectVariant}
        />
      )}

      {/* View Toggle - positioned at top left */}
      <div className="absolute left-8 top-8 z-10">
        <ViewToggle activeView={activeView} onViewChange={setActiveView} />
      </div>

      {/* Phase Bar - positioned at top center (only in node-editor view) */}
      {activeView === 'node-editor' && (
        <div className="absolute left-1/2 top-8 z-10 -translate-x-1/2">
          <PhaseBar phases={phases} onPhaseClick={setActivePhase} />
        </div>
      )}

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
        /* Chart View */
        <div className="h-full w-full overflow-y-auto bg-gray-50 px-8 pt-24 pb-8">
          <div className="mx-auto max-w-7xl space-y-6">
            {/* Welcome Bar */}
            <WelcomeBar />

            {/* Charts Grid */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Line Chart */}
              <EngagementLineChart />

              {/* Pie Chart */}
              <EngagementPieChart />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
