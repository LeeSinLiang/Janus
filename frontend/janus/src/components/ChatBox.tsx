'use client';

import { useState, useRef, useEffect } from 'react';
import { Node } from '@xyflow/react';

interface RejectionState {
  nodeId: string;
  nodeName: string;
}

interface ChatBoxProps {
  nodes: Node[];
  rejectionState?: RejectionState | null;
  onRejectionSubmit?: (rejectMessage: string) => void;
  onCancelRejection?: () => void;
}

export default function ChatBox({
  nodes,
  rejectionState,
  onRejectionSubmit,
  onCancelRejection
}: ChatBoxProps) {
  const [message, setMessage] = useState('');
  const [showMentionMenu, setShowMentionMenu] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [mentionPosition, setMentionPosition] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus textarea when rejection mode is activated
  useEffect(() => {
    if (rejectionState && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [rejectionState]);

  // Extract node titles for the mention menu
  const nodeOptions = nodes.map((node) => ({
    id: node.id,
    title: (node.data?.title as string) || 'Untitled',
  }));

  // Handle @ detection
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPosition = e.target.selectionStart;

    setMessage(value);

    // Check if @ was just typed
    const beforeCursor = value.slice(0, cursorPosition);
    const lastAtIndex = beforeCursor.lastIndexOf('@');

    if (lastAtIndex !== -1) {
      const afterAt = beforeCursor.slice(lastAtIndex + 1);
      // Show menu if @ is at the start or after a space, and no space after @
      if ((lastAtIndex === 0 || beforeCursor[lastAtIndex - 1] === ' ') && !afterAt.includes(' ')) {
        setShowMentionMenu(true);
        setMentionPosition(lastAtIndex);
        setSelectedIndex(0);
      } else {
        setShowMentionMenu(false);
      }
    } else {
      setShowMentionMenu(false);
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (showMentionMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % nodeOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + nodeOptions.length) % nodeOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectNode(nodeOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowMentionMenu(false);
      }
      return;
    }

    // Handle Enter key for message submission
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }

    // Handle Escape key to cancel rejection mode
    if (e.key === 'Escape' && rejectionState) {
      e.preventDefault();
      onCancelRejection?.();
    }
  };

  // Handle message submission
  const handleSubmit = () => {
    if (!message.trim()) return;

    if (rejectionState) {
      // In rejection mode - submit rejection
      onRejectionSubmit?.(message.trim());
      setMessage('');
    } else {
      // Normal message mode - handle normally (you can implement this later)
      console.log('Sin is so corny bhai macha:', message);
      setMessage('');
    }
  };

  // Select a node from the menu
  const selectNode = (node: { id: string; title: string }) => {
    const beforeMention = message.slice(0, mentionPosition);
    const afterMention = message.slice(mentionPosition + 1);

    // Remove any partial typing after @
    const cleanAfter = afterMention.replace(/^[^\s]*/, '');

    const newMessage = `${beforeMention}[${node.title}] ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowMentionMenu(false);

    // Focus back on textarea
    textareaRef.current?.focus();
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (showMentionMenu && textareaRef.current && !textareaRef.current.contains(target)) {
        setShowMentionMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showMentionMenu]);

  return (
    <div className="w-full px-6 py-4">
      <div className="mx-auto">
        {/* Rejection mode banner */}
        {rejectionState && (
          <div className="mb-3 rounded-lg bg-red-50 border border-red-200 px-4 py-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-semibold text-red-900">
                  Rejecting node: {rejectionState.nodeName}
                </span>
                <p className="mt-1 text-xs text-red-700">
                  Provide suggestion to better the strategy!
                </p>
              </div>
              <button
                onClick={onCancelRejection}
                className="text-red-600 hover:text-red-800 transition-colors"
                title="Cancel rejection"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Current prompt display */}
        {!rejectionState && (
          <div className="mb-3">
            <span className="text-base font-semibold text-[#FCD34D]">Janus:</span>
            <span className="ml-2 text-sm text-zinc-700">
              How can I help with your marketing roadmap?
            </span>
          </div>
        )}

        {/* Context button */}
        {!rejectionState && (
          <div className="mb-2">
            <button className="rounded-full border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs text-zinc-600 transition-colors hover:bg-zinc-100">
              @ to add context
            </button>
          </div>
        )}

        {/* Input area */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleMessageChange}
            onKeyDown={handleKeyDown}
            placeholder={rejectionState ? "Explain why you're rejecting this node..." : "Change triggers for marketing strategy..."}
            className={`w-full resize-none rounded-lg border px-3 py-2 pr-32 text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-1 ${
              rejectionState
                ? 'border-red-300 bg-red-50 focus:border-red-400 focus:ring-red-400'
                : 'border-zinc-200 bg-white focus:border-zinc-300 focus:ring-zinc-300'
            }`}
            rows={rejectionState ? 3 : 1}
          />

          {/* Mention Menu */}
          {showMentionMenu && nodeOptions.length > 0 && (
            <div className="absolute bottom-full left-0 mb-2 w-64 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
              <div className="max-h-48 overflow-y-auto">
                {nodeOptions.map((node, index) => (
                  <button
                    key={node.id}
                    onClick={() => selectNode(node)}
                    className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                      index === selectedIndex
                        ? 'bg-blue-50 text-blue-900'
                        : 'text-zinc-900 hover:bg-zinc-50'
                    }`}
                  >
                    {node.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Bottom toolbar */}
          <div className="mt-2 flex items-center justify-end">
            <div className="flex items-right gap-2">
              {/* Image icon */}
              <button className="text-zinc-400 transition-colors hover:text-zinc-600">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </button>

              {/* Video play icon */}
              <button className="text-zinc-400 transition-colors hover:text-zinc-600">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              </button>

              {/* Send button */}
              <button
                onClick={handleSubmit}
                className={`rounded-lg p-1.5 text-white transition-colors ${
                  rejectionState
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-zinc-900 hover:bg-zinc-700'
                }`}
                title={rejectionState ? 'Submit rejection' : 'Send message'}
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
