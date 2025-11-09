'use client';

import { Handle, Position } from '@xyflow/react';
import { THEME_COLORS, getButtonStyle, getNodeHighlightStyle } from '@/styles/theme';

export interface Variant {
  title: string;
  description: string;
}

export interface TaskCardData {
  icon: string;
  iconBg: string;
  title: string;
  description: string;
  likes: number;
  comments: number;
  tags: Array<{ label: string; color: string }>;
  pendingApproval?: boolean;
  onApprove?: () => void;
  onReject?: () => void;
  onClick?: (event?: MouseEvent) => void;
  variant1?: Variant;
  variant2?: Variant;
  isSelected?: boolean;
}

interface TaskCardNodeProps {
  data: TaskCardData;
  id: string;
}

export default function TaskCardNode({ data, id }: TaskCardNodeProps) {
  const isPending = data.pendingApproval || false;
  const isSelected = data.isSelected || false;

  return (
    <div className="relative">
      {/* Approve/Reject buttons - positioned above the card */}
      {isPending && (
        <div className="absolute -top-16 right-2 z-10 flex gap-2">
          {/* Approve button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              data.onApprove?.();
            }}
            style={getButtonStyle('approve')}
            className="flex h-12 w-12 items-center justify-center rounded-xl shadow-md transition-all hover:opacity-90 hover:scale-110"
            title="Approve node"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-black"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </button>

          {/* Reject button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              data.onReject?.();
            }}
            style={getButtonStyle('reject')}
            className="flex h-12 w-12 items-center justify-center rounded-xl shadow-md transition-all hover:opacity-90 hover:scale-110"
            title="Reject node"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-black"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      )}

      <div
        onClick={(e) => {
          e.stopPropagation();
          data.onClick?.(e.nativeEvent);
        }}
        className={`w-[300px] rounded-lg p-4 shadow-md transition-all cursor-pointer hover:shadow-lg`}
        style={
          isPending
            ? {
                background: THEME_COLORS.nodePendingBackground,
                ...getNodeHighlightStyle(),
              }
            : isSelected
            ? {
                background: '#F3E8FF', // Light purple fill
                border: '2px solid #A855F7', // Darker purple border
              }
            : {
                background: THEME_COLORS.nodeBackground,
                border: '1px solid #E5E7EB',
              }
        }
      >
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
            <span>🔄️</span>
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
    </div>
  );
}
