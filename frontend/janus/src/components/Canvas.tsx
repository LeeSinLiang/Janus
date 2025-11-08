'use client';

import { useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  BackgroundVariant,
  Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import TaskCardNode from './TaskCardNode';
import ChatBox from './ChatBox';

const nodeTypes = {
  taskCard: TaskCardNode,
};

// Available attribute tags
const ATTRIBUTES = {
  PLANNED: { label: 'Planned', color: '#FCD34D' },
  FEATURE: { label: 'Feature', color: '#9333EA' },
  FINISHED: { label: 'Finished', color: '#10B981' },
  PROMO: { label: 'Promo', color: '#3B82F6' },
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'taskCard',
    position: { x: 50, y: 50 },
    data: {
      icon: '📷',
      iconBg: '#E4405F',
      title: 'Instagram post',
      description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post',
      likes: 1,
      comments: 0,
      tags: [ATTRIBUTES.FEATURE, ATTRIBUTES.PLANNED],
    },
  },
  {
    id: '2',
    type: 'taskCard',
    position: { x: 50, y: 280 },
    data: {
      icon: '𝕏',
      iconBg: '#000000',
      title: 'X post',
      description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
      likes: 1,
      comments: 0,
      tags: [ATTRIBUTES.PROMO, ATTRIBUTES.PLANNED],
    },
  },
  {
    id: '3',
    type: 'taskCard',
    position: { x: 500, y: 50 },
    data: {
      icon: '📷',
      iconBg: '#E4405F',
      title: 'Instagram reels',
      description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post',
      likes: 1,
      comments: 0,
      tags: [ATTRIBUTES.FEATURE, ATTRIBUTES.FINISHED],
    },
  },
  {
    id: '4',
    type: 'taskCard',
    position: { x: 500, y: 330 },
    data: {
      icon: '▶️',
      iconBg: '#FF0000',
      title: 'Youtube shorts',
      description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post',
      likes: 1,
      comments: 0,
      tags: [ATTRIBUTES.FEATURE, ATTRIBUTES.PLANNED],
    },
  },
  {
    id: '5',
    type: 'taskCard',
    position: { x: 950, y: 150 },
    data: {
      icon: '▶️',
      iconBg: '#FF0000',
      title: 'Video marketing',
      description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post',
      likes: 1,
      comments: 0,
      tags: [ATTRIBUTES.PROMO, ATTRIBUTES.FINISHED],
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#94A3B8', strokeWidth: 2 },
  },
  {
    id: 'e1-3',
    source: '1',
    target: '3',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#94A3B8', strokeWidth: 2, strokeDasharray: '5,5' },
  },
  {
    id: 'e3-5',
    source: '3',
    target: '5',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#94A3B8', strokeWidth: 2 },
  },
  {
    id: 'e4-5',
    source: '4',
    target: '5',
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#94A3B8', strokeWidth: 2 },
  },
];

export default function Canvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

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

  return (
    <div className="relative h-full w-full bg-gray-50">
      {/* ReactFlow Canvas */}
      <ReactFlow
        nodes={nodes}
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
          <ChatBox nodes={nodes} />
        </div>
      </div>
    </div>
  );
}
