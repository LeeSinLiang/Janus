'use client';

import { Handle, Position } from '@xyflow/react';

export interface TaskCardData {
  icon: string;
  iconBg: string;
  title: string;
  description: string;
  likes: number;
  comments: number;
  tags: Array<{ label: string; color: string }>;
}

interface TaskCardNodeProps {
  data: TaskCardData;
}

export default function TaskCardNode({ data }: TaskCardNodeProps) {
  return (
    <div className="w-[300px] rounded-lg border border-zinc-200 bg-white p-4 shadow-md">
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !bg-zinc-400"
      />

      <div className="mb-3 flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-lg"
          style={{ backgroundColor: data.iconBg }}
        >
          <span className="text-xl">{data.icon}</span>
        </div>
        <h3 className="text-lg font-semibold text-zinc-900">
          {data.title}
        </h3>
      </div>

      <p className="mb-4 text-sm leading-relaxed text-zinc-600">
        {data.description}
      </p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-sm">
          <span className="flex items-center gap-1">
            <span>👍</span>
            <span className="text-zinc-700">{data.likes}</span>
          </span>
          <span className="flex items-center gap-1">
            <span>💬</span>
            <span className="text-zinc-700">{data.comments}</span>
          </span>
        </div>

        <div className="flex gap-2">
          {data.tags.map((tag, index) => (
            <span
              key={index}
              className="rounded px-2 py-1 text-xs font-medium"
              style={{
                backgroundColor: tag.color,
                color: tag.color === '#FCD34D' ? '#000' : '#fff',
              }}
            >
              {tag.label}
            </span>
          ))}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !bg-zinc-400"
      />
    </div>
  );
}
