'use client';

import { useState, useRef, useEffect } from 'react';
import { Node } from '@xyflow/react';
import { parseTrigger, sendMultiNodePrompt, regenerateStrategy } from '@/services/api';
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
  campaignId?: string;
}

export default function ChatBox({
  nodes,
  rejectionState,
  onRejectionSubmit,
  onCancelRejection,
  selectedNodeIds = new Set(),
  onMultiNodeSubmit,
  campaignId
}: ChatBoxProps) {
  const [message, setMessage] = useState('');
  const [showMentionMenu, setShowMentionMenu] = useState(false);
  const [showCommandMenu, setShowCommandMenu] = useState(false);
  const [showPhaseMenu, setShowPhaseMenu] = useState(false);
  const [showThresholdMenu, setShowThresholdMenu] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [mentionPosition, setMentionPosition] = useState(0);
  const [commandPosition, setCommandPosition] = useState(0);
  const [phasePosition, setPhasePosition] = useState(0);
  const [thresholdPosition, setThresholdPosition] = useState(0);
  const [mentionedNodeTitle, setMentionedNodeTitle] = useState<string | null>(null);
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
    { id: 'regenerate', label: 'Regenerate strategy from phase', value: 'regenerate' }
  ];

  // Phase options for /regenerate command
  const phaseOptions = [
    { id: 'phase1', label: 'Phase 1', value: '1' },
    { id: 'phase2', label: 'Phase 2', value: '2' },
    { id: 'phase3', label: 'Phase 3', value: '3' }
  ];

  // Threshold options for post-@ mention
  const thresholdOptions = [
    { id: 'likes', label: 'Likes', value: 'likes' },
    { id: 'retweets', label: 'Retweets', value: 'retweets' },
    { id: 'impressions', label: 'Impressions', value: 'impressions' },
    { id: 'comments', label: 'Comments', value: 'comments' }
  ];

  // Handle @ and / detection
  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPosition = e.target.selectionStart;

    setMessage(value);

    const beforeCursor = value.slice(0, cursorPosition);

    // Check for phase menu after /regenerate
    const regeneratePhaseRegex = /\/regenerate\s+(?:phase\s*)?$/i;
    if (regeneratePhaseRegex.test(beforeCursor)) {
      const phaseKeywordIndex = beforeCursor.toLowerCase().lastIndexOf('phase');
      setPhasePosition(phaseKeywordIndex !== -1 ? phaseKeywordIndex : beforeCursor.length);
      setShowPhaseMenu(true);
      setShowCommandMenu(false);
      setShowMentionMenu(false);
      setShowThresholdMenu(false);
      setSelectedIndex(0);
      return;
    }

    // Check for phase menu continuation (user is typing phase number)
    const regeneratePhaseTypingRegex = /\/regenerate\s+phase\s+\d*$/i;
    if (regeneratePhaseTypingRegex.test(beforeCursor)) {
      const phaseKeywordIndex = beforeCursor.toLowerCase().lastIndexOf('phase');
      setPhasePosition(phaseKeywordIndex + 'phase '.length);
      setShowPhaseMenu(true);
      setShowCommandMenu(false);
      setShowMentionMenu(false);
      setShowThresholdMenu(false);
      setSelectedIndex(0);
      return;
    }

    // Check for threshold menu after @NodeTitle
    if (mentionedNodeTitle) {
      const mentionPattern = new RegExp(`@${mentionedNodeTitle}\\s+(?!\\()([^\\s(]*)$`);
      const thresholdMatch = beforeCursor.match(mentionPattern);

      if (thresholdMatch) {
        const thresholdStartIndex = beforeCursor.lastIndexOf(thresholdMatch[1]);
        setThresholdPosition(thresholdStartIndex);
        setShowThresholdMenu(true);
        setShowCommandMenu(false);
        setShowMentionMenu(false);
        setShowPhaseMenu(false);
        setSelectedIndex(0);
        return;
      }
    }

    // Check for / command
    const lastSlashIndex = beforeCursor.lastIndexOf('/');
    if (lastSlashIndex !== -1) {
      const afterSlash = beforeCursor.slice(lastSlashIndex + 1);
      // Show command menu if / is at the start or after a space, and no space after /
      if ((lastSlashIndex === 0 || beforeCursor[lastSlashIndex - 1] === ' ') && !afterSlash.includes(' ')) {
        setShowCommandMenu(true);
        setCommandPosition(lastSlashIndex);
        setShowMentionMenu(false);
        setShowPhaseMenu(false);
        setShowThresholdMenu(false);
        setSelectedIndex(0);
        return;
      }
    }

    // Check for @ mention
    const lastAtIndex = beforeCursor.lastIndexOf('@');
    if (lastAtIndex !== -1) {
      const afterAt = beforeCursor.slice(lastAtIndex + 1);
      // Show menu if @ is at the start or after a space, and no space/( after @
      if ((lastAtIndex === 0 || beforeCursor[lastAtIndex - 1] === ' ') && !afterAt.includes(' ') && !afterAt.includes('(')) {
        setShowMentionMenu(true);
        setMentionPosition(lastAtIndex);
        setShowCommandMenu(false);
        setShowPhaseMenu(false);
        setShowThresholdMenu(false);
        setSelectedIndex(0);
        return;
      }
    }

    // Close all menus if no condition is met
    setShowMentionMenu(false);
    setShowCommandMenu(false);
    setShowPhaseMenu(false);
    setShowThresholdMenu(false);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Get filtered options based on current context
    const beforeCursor = message.slice(0, textareaRef.current?.selectionStart || 0);

    if (showMentionMenu) {
      const lastAtIndex = beforeCursor.lastIndexOf('@');
      const afterAt = beforeCursor.slice(lastAtIndex + 1);
      const filteredNodeOptions = nodeOptions.filter(node =>
        node.title.toLowerCase().includes(afterAt.toLowerCase())
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredNodeOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredNodeOptions.length) % filteredNodeOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectNode(filteredNodeOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowMentionMenu(false);
      }
      return;
    }

    if (showCommandMenu) {
      const lastSlashIndex = beforeCursor.lastIndexOf('/');
      const afterSlash = beforeCursor.slice(lastSlashIndex + 1);
      const filteredCommandOptions = commandOptions.filter(cmd =>
        cmd.label.toLowerCase().includes(afterSlash.toLowerCase()) ||
        cmd.value.toLowerCase().includes(afterSlash.toLowerCase())
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredCommandOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommandOptions.length) % filteredCommandOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectCommand(filteredCommandOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowCommandMenu(false);
      }
      return;
    }

    if (showPhaseMenu) {
      const afterPhase = message.slice(phasePosition);
      const searchTerm = afterPhase.split(/[\s]/)[0];
      const filteredPhaseOptions = phaseOptions.filter(opt =>
        opt.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        opt.value.toLowerCase().includes(searchTerm.toLowerCase())
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredPhaseOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredPhaseOptions.length) % filteredPhaseOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectPhase(filteredPhaseOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowPhaseMenu(false);
      }
      return;
    }

    if (showThresholdMenu) {
      const afterMention = message.slice(thresholdPosition);
      const searchTerm = afterMention.split(/[\s(]/)[0];
      const filteredThresholdOptions = thresholdOptions.filter(opt =>
        opt.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        opt.value.toLowerCase().includes(searchTerm.toLowerCase())
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredThresholdOptions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredThresholdOptions.length) % filteredThresholdOptions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectThreshold(filteredThresholdOptions[selectedIndex]);
      } else if (e.key === 'Escape') {
        setShowThresholdMenu(false);
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
      // Check for /regenerate phase X <prompt> command
      const regenerateRegex = /^\/regenerate\s+phase\s+(\d+)\s+(.+)$/i;
      const regenerateMatch = message.trim().match(regenerateRegex);

      if (regenerateMatch && campaignId) {
        const phaseNum = parseInt(regenerateMatch[1]);
        const newDirection = regenerateMatch[2].trim();

        // Validate phase number
        if (phaseNum < 1 || phaseNum > 3) {
          console.error('Invalid phase number. Must be 1, 2, or 3.');
          setMessage('');
          return;
        }

        try {
          const result = await regenerateStrategy(campaignId, phaseNum, newDirection);
          console.log(`Strategy regeneration started for Phase ${phaseNum}:`, result);

          // Clear message on success
          setMessage('');
        } catch (error) {
          console.error('Failed to regenerate strategy:', error);
        }
        return;
      }

      // Check for missing campaign ID when using /regenerate command
      if (regenerateMatch && !campaignId) {
        console.error('Cannot regenerate strategy without a campaign ID');
        setMessage('');
        return;
      }

      // Normal message mode - parse for trigger in format: @NodeTitle (condition) prompt
      // Updated regex to support spaces in node titles using non-greedy match
      const triggerRegex = /@([^(]+?)\s*\((\w+)\)\s*(.+)$/;
      const triggerMatch = message.trim().match(triggerRegex);

      if (triggerMatch) {
        const nodeTitle = triggerMatch[1].trim(); // Trim to remove trailing spaces
        const condition = triggerMatch[2];
        const prompt = triggerMatch[3].trim();

        console.log('Trigger regex matched:', { nodeTitle, condition, prompt });

        // Validate condition is one of the allowed values
        const validConditions: Array<'likes' | 'retweets' | 'impressions' | 'comments'> = [
          'likes',
          'retweets',
          'impressions',
          'comments',
        ];

        if (validConditions.includes(condition as 'likes' | 'retweets' | 'impressions' | 'comments')) {
          // Find node pk by title
          const node = nodeOptions.find(n => n.title === nodeTitle);

          if (node && prompt) {
            const nodePk = parseInt(node.id);

            console.log(`Sending trigger to backend: pk=${nodePk}, condition=${condition}, prompt="${prompt}"`);

            try {
              const result = await parseTrigger(
                nodePk,
                condition as 'likes' | 'retweets' | 'impressions' | 'comments',
                prompt
              );
              console.log(`✓ Trigger parsed and saved for node ${nodePk}:`, result);
              setMessage('');
              return;
            } catch (error) {
              console.error('✗ Failed to parse trigger:', error);
              setMessage('');
              return;
            }
          } else {
            console.error('Trigger validation failed:', { node: node ? 'found' : 'NOT FOUND', hasPrompt: !!prompt });
          }
        } else {
          console.error('Invalid condition:', condition, 'Valid:', validConditions);
        }
      } else {
        console.log('Trigger regex did not match. Message:', message.trim());
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

    const newMessage = `${beforeMention}@${node.title} ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowMentionMenu(false);

    // Store node title and trigger threshold menu
    setMentionedNodeTitle(node.title);
    setThresholdPosition(beforeMention.length + node.title.length + 2); // Position after "@NodeTitle "
    setShowThresholdMenu(true);
    setSelectedIndex(0);

    // Focus back on textarea
    textareaRef.current?.focus();
  };

  // Select a command from the menu
  const selectCommand = (command: { id: string; label: string; value: string }) => {
    const beforeCommand = message.slice(0, commandPosition);
    const afterCommand = message.slice(commandPosition + 1);

    // Remove any partial typing after /
    const cleanAfter = afterCommand.replace(/^[^\s]*/, '');

    if (command.value === 'regenerate') {
      // For regenerate command, insert "/regenerate " and trigger phase menu
      const newMessage = `${beforeCommand}/regenerate ${cleanAfter}`.trim() + ' ';
      setMessage(newMessage);
      setShowCommandMenu(false);

      // Trigger phase menu
      setPhasePosition(beforeCommand.length + '/regenerate '.length);
      setShowPhaseMenu(true);
      setSelectedIndex(0);
    } else {
      // For other commands (if any in future)
      const newMessage = `${beforeCommand}/${command.value} ${cleanAfter}`.trim() + ' ';
      setMessage(newMessage);
      setShowCommandMenu(false);
    }

    // Focus back on textarea
    textareaRef.current?.focus();
  };

  // Select a phase from the menu
  const selectPhase = (phase: { id: string; label: string; value: string }) => {
    // Find where "/regenerate " ends
    const regenerateIndex = message.lastIndexOf('/regenerate ');
    if (regenerateIndex === -1) return;

    const beforePhase = message.slice(0, regenerateIndex + '/regenerate '.length);
    const afterPhase = message.slice(regenerateIndex + '/regenerate '.length);

    // Remove any partial typing after phase keyword
    const cleanAfter = afterPhase.replace(/^(?:phase\s*)?\d*/, '').trim();

    const newMessage = `${beforePhase}phase ${phase.value} ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowPhaseMenu(false);

    textareaRef.current?.focus();
  };

  // Select a threshold from the menu
  const selectThreshold = (threshold: { id: string; label: string; value: string }) => {
    const beforeThreshold = message.slice(0, thresholdPosition);
    const afterThreshold = message.slice(thresholdPosition);

    // Remove any partial typing
    const cleanAfter = afterThreshold.replace(/^[^\s]*/, '');

    const newMessage = `${beforeThreshold}(${threshold.value}) ${cleanAfter}`.trim() + ' ';
    setMessage(newMessage);
    setShowThresholdMenu(false);
    setMentionedNodeTitle(null);

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
      if (showPhaseMenu && textareaRef.current && !textareaRef.current.contains(target)) {
        setShowPhaseMenu(false);
      }
      if (showThresholdMenu && textareaRef.current && !textareaRef.current.contains(target)) {
        setShowThresholdMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showMentionMenu, showCommandMenu, showPhaseMenu, showThresholdMenu]);

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
          {showMentionMenu && nodeOptions.length > 0 && (() => {
            const beforeCursor = message.slice(0, textareaRef.current?.selectionStart || 0);
            const lastAtIndex = beforeCursor.lastIndexOf('@');
            const afterAt = beforeCursor.slice(lastAtIndex + 1);
            const filteredNodeOptions = nodeOptions.filter(node =>
              node.title.toLowerCase().includes(afterAt.toLowerCase())
            );

            return filteredNodeOptions.length > 0 ? (
              <div className="absolute bottom-full left-0 mb-2 w-64 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
                <div className="max-h-48 overflow-y-auto">
                  {filteredNodeOptions.map((node, index) => (
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
            ) : null;
          })()}

          {/* Command Menu */}
          {showCommandMenu && commandOptions.length > 0 && (() => {
            const beforeCursor = message.slice(0, textareaRef.current?.selectionStart || 0);
            const lastSlashIndex = beforeCursor.lastIndexOf('/');
            const afterSlash = beforeCursor.slice(lastSlashIndex + 1);
            const filteredCommandOptions = commandOptions.filter(cmd =>
              cmd.label.toLowerCase().includes(afterSlash.toLowerCase()) ||
              cmd.value.toLowerCase().includes(afterSlash.toLowerCase())
            );

            return filteredCommandOptions.length > 0 ? (
              <div className="absolute bottom-full left-0 mb-2 w-64 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
                <div className="max-h-48 overflow-y-auto">
                  {filteredCommandOptions.map((command, index) => (
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
            ) : null;
          })()}

          {/* Phase Menu */}
          {showPhaseMenu && phaseOptions.length > 0 && (() => {
            const afterPhase = message.slice(phasePosition);
            const searchTerm = afterPhase.split(/[\s]/)[0];
            const filteredPhaseOptions = phaseOptions.filter(opt =>
              opt.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
              opt.value.toLowerCase().includes(searchTerm.toLowerCase())
            );

            return filteredPhaseOptions.length > 0 ? (
              <div className="absolute bottom-full left-0 mb-2 w-48 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
                <div className="max-h-48 overflow-y-auto">
                  {filteredPhaseOptions.map((phase, index) => (
                    <button
                      key={phase.id}
                      onClick={() => selectPhase(phase)}
                      className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                        index === selectedIndex
                          ? 'bg-blue-50 text-blue-900'
                          : 'text-zinc-900 hover:bg-zinc-50'
                      }`}
                    >
                      {phase.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : null;
          })()}

          {/* Threshold Menu */}
          {showThresholdMenu && thresholdOptions.length > 0 && (() => {
            const afterMention = message.slice(thresholdPosition);
            const searchTerm = afterMention.split(/[\s(]/)[0];
            const filteredThresholdOptions = thresholdOptions.filter(opt =>
              opt.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
              opt.value.toLowerCase().includes(searchTerm.toLowerCase())
            );

            return filteredThresholdOptions.length > 0 ? (
              <div className="absolute bottom-full left-0 mb-2 w-48 overflow-hidden rounded-lg border border-zinc-200 bg-white shadow-lg">
                <div className="max-h-48 overflow-y-auto">
                  {filteredThresholdOptions.map((threshold, index) => (
                    <button
                      key={threshold.id}
                      onClick={() => selectThreshold(threshold)}
                      className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                        index === selectedIndex
                          ? 'bg-blue-50 text-blue-900'
                          : 'text-zinc-900 hover:bg-zinc-50'
                      }`}
                    >
                      {threshold.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : null;
          })()}


        </div>
      </div>
    </div>
  );
}
