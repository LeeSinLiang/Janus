'use client';

import { useState, useRef, useEffect } from 'react';
import { Node } from '@xyflow/react';
import { parseTrigger, sendMultiNodePrompt } from '@/services/api';
import TypingText from './TypingText';

interface RejectionState {
  nodeId: string;
  nodeName: string;
}

interface ChatBoxProps {
  nodes: Node[];
  rejectionState?: RejectionState | null;
  onRejectionSubmit?: (rejectMessage: string) => void;
  onCancelRejection?: () => void;
  selectedNodeIds?: Set<string>;
  onMultiNodeSubmit?: () => void;
}

export default function ChatBox({
  nodes,
  rejectionState,
  onRejectionSubmit,
  onCancelRejection,
  selectedNodeIds = new Set(),
  onMultiNodeSubmit
}: ChatBoxProps) {
  const [message, setMessage] = useState('');
  const [showMentionMenu, setShowMentionMenu] = useState(false);
  const [showCommandMenu, setShowCommandMenu] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [mentionPosition, setMentionPosition] = useState(0);
  const [commandPosition, setCommandPosition] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Typing animation state
  const [showRequestSent, setShowRequestSent] = useState(false);
  const [typingKey, setTypingKey] = useState(0); // Force re-render of typing animation

  // Auto-focus textarea when rejection mode is activated
  useEffect(() => {
    if (rejectionState && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [rejectionState]);

  // Reset to default message after 15 seconds
  useEffect(() => {
    if (showRequestSent) {
      const timer = setTimeout(() => {
        setShowRequestSent(false);
        setTypingKey(prev => prev + 1); // Force re-render typing animation
      }, 15000);

      return () => clearTimeout(timer);
    }
  }, [showRequestSent]);

  // Extract node titles for the mention menu
  const nodeOptions = nodes.map((node) => ({
    id: node.id,
    title: (node.data?.title as string) || 'Untitled',
  }));

  // Command options for / menu
  const commandOptions = [
    { id: 'likes', label: 'Likes threshold', value: 'likes' },
    { id: 'retweets', label: 'Retweets threshold', value: 'retweets' },
    { id: 'impressions', label: 'Impressions threshold', value: 'impressions' },
    { id: 'comments', label: 'Comments threshold', value: 'comments' },
  ];

  // Handle @ and / detection
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPosition = e.target.selectionStart;

    setMessage(value);

    const beforeCursor = value.slice(0, cursorPosition);

    // Check for / command
    const lastSlashIndex = beforeCursor.lastIndexOf('/');
    if (lastSlashIndex !== -1) {
      const afterSlash = beforeCursor.slice(lastSlashIndex + 1);
      // Show command menu if / is at the start or after a space, and no space after /
      if ((lastSlashIndex === 0 || beforeCursor[lastSlashIndex - 1] === ' ') && !afterSlash.includes(' ')) {
        setShowCommandMenu(true);
        setCommandPosition(lastSlashIndex);
        setShowMentionMenu(false);
        setSelectedIndex(0);
        return;
      }
    }

    // Check for @ mention
    const lastAtIndex = beforeCursor.lastIndexOf('@');
    if (lastAtIndex !== -1) {
      const afterAt = beforeCursor.slice(lastAtIndex + 1);
      // Show menu if @ is at the start or after a space, and no space after @
      if ((lastAtIndex === 0 || beforeCursor[lastAtIndex - 1] === ' ') && !afterAt.includes(' ')) {
        setShowMentionMenu(true);
        setMentionPosition(lastAtIndex);
        setShowCommandMenu(false);
        setSelectedIndex(0);
        return;
      }
    }

    // Close both menus if neither condition is met
    setShowMentionMenu(false);
    setShowCommandMenu(false);
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

    if (showCommandMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % commandOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + commandOptions.length) % commandOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectCommand(commandOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowCommandMenu(false);
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
  const handleSubmit = async () => {
    if (!message.trim()) return;

    // Trigger typing animation
    setShowRequestSent(true);
    setTypingKey(prev => prev + 1);

    if (rejectionState) {
      // In rejection mode - submit rejection
      onRejectionSubmit?.(message.trim());
      setMessage('');
    } else if (selectedNodeIds.size > 0) {
      // Multi-node selection mode - send to sintodo
      const nodePks = Array.from(selectedNodeIds).map(id => parseInt(id));

      try {
        await sendMultiNodePrompt(nodePks, message.trim());
        console.log(`Multi-node prompt sent for nodes: ${nodePks.join(', ')}`);

        // Clear message and notify parent to clear selections
        setMessage('');
        onMultiNodeSubmit?.();
      } catch (error) {
        console.error('Failed to send multi-node prompt:', error);
      }
    } else {
      // Normal message mode - parse for trigger in format: **NodeTitle** **condition** prompt
      // Extract all **text** patterns
      const boldTextMatches = message.match(/\*\*([^*]+)\*\*/g);

      if (boldTextMatches && boldTextMatches.length >= 2) {
        // Extract node title (first bold text)
        const nodeTitle = boldTextMatches[0].replace(/\*\*/g, '');

        // Extract condition (second bold text)
        const condition = boldTextMatches[1].replace(/\*\*/g, '');

        // Validate condition is one of the allowed values
        const validConditions: Array<'likes' | 'retweets' | 'impressions' | 'comments'> = [
          'likes',
          'retweets',
          'impressions',
          'comments',
        ];

        if (validConditions.includes(condition as any)) {
          // Find node pk by title
          const node = nodeOptions.find(n => n.title === nodeTitle);

          if (node) {
            // Extract prompt (everything after the second **condition**)
            const promptStartIndex = message.indexOf(boldTextMatches[1]) + boldTextMatches[1].length;
            const prompt = message.slice(promptStartIndex).trim();

            if (prompt) {
              const nodePk = parseInt(node.id);

              try {
                const result = await parseTrigger(
                  nodePk,
                  condition as 'likes' | 'retweets' | 'impressions' | 'comments',
                  prompt
                );
                console.log(`Trigger parsed and saved for node ${nodePk}:`, result);
              } catch (error) {
                console.error('Failed to parse trigger:', error);
              }
            } else {
              console.log('No prompt provided after condition');
            }
          } else {
            console.log(`Node with title "${nodeTitle}" not found`);
          }
        } else {
          console.log(`Invalid condition "${condition}". Must be one of: ${validConditions.join(', ')}`);
        }
      }

      setMessage('');
    }
  };

  // Select a node from the menu
  const selectNode = (node: { id: string; title: string }) => {
    const beforeMention = message.slice(0, mentionPosition);
    const afterMention = message.slice(mentionPosition + 1);

    // Remove any partial typing after @
    const cleanAfter = afterMention.replace(/^[^\s]*/, '');

    const newMessage = `${beforeMention}**${node.title}** ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowMentionMenu(false);

    // Focus back on textarea
    textareaRef.current?.focus();
  };

  // Select a command from the menu
  const selectCommand = (command: { id: string; label: string; value: string }) => {
    const beforeCommand = message.slice(0, commandPosition);
    const afterCommand = message.slice(commandPosition + 1);

    // Remove any partial typing after /
    const cleanAfter = afterCommand.replace(/^[^\s]*/, '');

    const newMessage = `${beforeCommand}**${command.value}** ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowCommandMenu(false);

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
      if (showCommandMenu && textareaRef.current && !textareaRef.current.contains(target)) {
        setShowCommandMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showMentionMenu, showCommandMenu]);

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
              {showRequestSent ? (
                <TypingText
                  key={`request-sent-${typingKey}`}
                  text="Request Sent!"
                  speed={40}
                  className="text-sm text-zinc-700"
                />
              ) : (
                <TypingText
                  key={`default-${typingKey}`}
                  text={
                    selectedNodeIds.size > 0
                      ? `${selectedNodeIds.size} node${selectedNodeIds.size > 1 ? 's' : ''} selected. What would you like to improve?`
                      : 'How can I help with your marketing roadmap?'
                  }
                  speed={40}
                  className="text-sm text-zinc-700"
                />
              )}
            </span>
          </div>
        )}

        {/* Context buttons and Send button */}
        {!rejectionState && (
          <div className="mb-2 flex items-center justify-between">
            <div className="flex gap-2">
              <button className="rounded-full border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs text-zinc-600 transition-colors hover:bg-zinc-100">
                @ to add context
              </button>
              <button className="rounded-full border border-zinc-200 bg-zinc-50 px-2.5 py-1 text-xs text-zinc-600 transition-colors hover:bg-zinc-100">
                / for commands
              </button>
            </div>
            {/* Send button */}
            <button
              onClick={handleSubmit}
              className={`rounded-lg p-1.5 text-white transition-colors ${
                selectedNodeIds.size > 0
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-zinc-900 hover:bg-zinc-700'
              }`}
              title={selectedNodeIds.size > 0 ? 'Send suggestion' : 'Send message'}
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
        )}

        {/* Input area */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleMessageChange}
            onKeyDown={handleKeyDown}
            placeholder={
              rejectionState
                ? "Explain why you're rejecting this node..."
                : selectedNodeIds.size > 0
                ? "Enter your suggestion for the selected nodes..."
                : "Change triggers for marketing strategy..."
            }
            className={`w-full resize-none rounded-lg border px-3 py-2 pr-32 text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-1 ${
              rejectionState
                ? 'border-red-300 bg-red-50 focus:border-red-400 focus:ring-red-400'
                : selectedNodeIds.size > 0
                ? 'border-purple-300 bg-purple-50 focus:border-purple-400 focus:ring-purple-400'
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

          {/* Command Menu */}
          {showCommandMenu && commandOptions.length > 0 && (
            <div className="absolute bottom-full left-0 mb-2 w-48 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
              <div className="max-h-48 overflow-y-auto">
                {commandOptions.map((command, index) => (
                  <button
                    key={command.id}
                    onClick={() => selectCommand(command)}
                    className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                      index === selectedIndex
                        ? 'bg-blue-50 text-blue-900'
                        : 'text-zinc-900 hover:bg-zinc-50'
                    }`}
                  >
                    {command.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          
        </div>
      </div>
    </div>
  );
}
