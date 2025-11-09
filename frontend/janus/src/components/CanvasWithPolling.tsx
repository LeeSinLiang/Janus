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
import { approveNode, rejectNode, fetchVariants, selectVariant, createXPost, approveAllNodes } from '@/services/api';
import { Node as FlowNode } from '@xyflow/react';
import { THEME_COLORS } from '@/styles/theme';

const nodeTypes = {
  taskCard: TaskCardNode,
};

interface RejectionState {
  nodeId: string;
  nodeName: string;
}

interface CanvasWithPollingProps {
  campaignId?: string;
}

export default function CanvasWithPolling({ campaignId }: CanvasWithPollingProps) {
  // View state
  const [activeView, setActiveView] = useState<'node-editor' | 'chart'>('node-editor');

  // Rejection flow state
  const [rejectionState, setRejectionState] = useState<RejectionState | null>(null);

  // Modal state for viewing node variants
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null);
  const [variants, setVariants] = useState<any>(null);

  // Phase state
  const [activePhase, setActivePhase] = useState(1); // 0-indexed, so 1 = Phase 2

  // Success message state
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Approve all loading state
  const [isApprovingAll, setIsApprovingAll] = useState(false);

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
        // Call both APIs in parallel
        await Promise.all([
          approveNode(nodeId),
          createXPost(nodeId)
        ]);

        // Update UI - remove pending state and change status to published
        setNodes((nds) =>
          nds.map((node) =>
            node.id === nodeId
              ? {
                  ...node,
                  data: {
                    ...node.data,
                    pendingApproval: false,
                    tags: Array.isArray(node.data.tags)
                      ? node.data.tags.map((tag: any) =>
                          tag.label === 'Planned'
                            ? { label: 'Published', color: '#10B981' }
                            : tag
                        )
                      : [],
                  },
                }
              : node
          )
        );

        // Show success message
        setSuccessMessage('Node approved and posted to X!');
        setTimeout(() => setSuccessMessage(null), 3000);
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

  // Handle approve all drafts in campaign
  const handleApproveAll = useCallback(async () => {
    if (!campaignId) {
      console.error('No campaign ID provided');
      return;
    }

    setIsApprovingAll(true);
    try {
      const result = await approveAllNodes(campaignId);

      // Show success message with count
      setSuccessMessage(`Successfully approved and published ${result.approved_count} draft post(s)!`);
      setTimeout(() => setSuccessMessage(null), 3000);

      // Data will automatically refresh via polling
    } catch (error) {
      console.error('Failed to approve all nodes:', error);
      setSuccessMessage('Failed to approve all drafts');
      setTimeout(() => setSuccessMessage(null), 3000);
    } finally {
      setIsApprovingAll(false);
    }
  }, [campaignId]);

  // Handle node click to fetch and show variants
  const handleNodeClick = useCallback(async (node: FlowNode) => {
    console.log('Node clicked:', node.id, node);
    try {
      // Fetch variants from backend
      console.log('Fetching variants for node:', node.id);
      const data = await fetchVariants(node.id);
      console.log('Variants data received:', data);

      if (data.variants && data.variants.length >= 2) {
        console.log('Setting variants and opening modal');
        setVariants(data.variants);
        setSelectedNode(node);
      } else {
        console.log('Not enough variants:', data.variants?.length || 0);
      }
    } catch (error) {
      console.error('Failed to fetch variants:', error);
    }
  }, []);

  // Handle variant selection
  const handleSelectVariant = useCallback(async (variantNumber: 1 | 2) => {
    if (!selectedNode || !variants) return;

    // Get the selected variant from fetched data
    const selectedVariant = variants[variantNumber - 1];

    if (selectedVariant) {
      try {
        // Save selection to backend
        await selectVariant(selectedNode.id, selectedVariant.variant_id);

        // Update the node's description with the selected variant content (instant feedback)
        setNodes((nds) =>
          nds.map((node) =>
            node.id === selectedNode.id
              ? {
                  ...node,
                  data: {
                    ...node.data,
                    description: selectedVariant.content,
                    selectedVariantId: selectedVariant.variant_id,
                  },
                }
              : node
          )
        );
      } catch (error) {
        console.error('Failed to save variant selection:', error);
        // Still update UI for instant feedback even if backend fails
        setNodes((nds) =>
          nds.map((node) =>
            node.id === selectedNode.id
              ? {
                  ...node,
                  data: {
                    ...node.data,
                    description: selectedVariant.content,
                    selectedVariantId: selectedVariant.variant_id,
                  },
                }
              : node
          )
        );
      }
    }

    // Close modal and clear variants
    setSelectedNode(null);
    setVariants(null);
  }, [selectedNode, variants, setNodes]);

  // Count draft posts (nodes with pendingApproval)
  const draftCount = nodes.filter(node => node.data?.pendingApproval === true).length;

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

  return (
    <div className="relative h-full w-full bg-gray-50">
      {/* Success Message Toast */}
      {successMessage && (
        <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50 animate-fade-in">
          <div className="bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">{successMessage}</span>
          </div>
        </div>
      )}

      {/* Node Variant Modal */}
      {selectedNode && variants && variants.length >= 2 && (
        <NodeVariantModal
          isOpen={!!selectedNode}
          onClose={() => {
            setSelectedNode(null);
            setVariants(null);
          }}
          variant1={variants[0]}
          variant2={variants[1]}
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

      {/* Approve All Button - positioned at top right (only when there are drafts) */}
      {activeView === 'node-editor' && campaignId && draftCount > 0 && (
        <div className="absolute right-8 top-8 z-10">
          <button
            onClick={handleApproveAll}
            disabled={isApprovingAll}
            style={{
              background: THEME_COLORS.approveButton.background,
              border: `1px solid ${THEME_COLORS.approveButton.border}`,
            }}
            className={`
              px-6 py-3 rounded-xl font-medium text-black shadow-md
              transition-all duration-200
              ${isApprovingAll
                ? 'opacity-60 cursor-not-allowed'
                : 'hover:opacity-90 hover:scale-110 active:scale-95'
              }
            `}
          >
            {isApprovingAll ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Approving...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Approve All Drafts ({draftCount})
              </span>
            )}
          </button>
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
