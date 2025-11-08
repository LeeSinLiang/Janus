'use client';

interface ViewToggleProps {
  activeView: 'node-editor' | 'chart';
  onViewChange: (view: 'node-editor' | 'chart') => void;
}

export default function ViewToggle({ activeView, onViewChange }: ViewToggleProps) {
  return (
    <div className="inline-flex rounded-md bg-gray-200 p-1 shadow-lg">
      {/* Node Editor Button */}
      <button
        onClick={() => onViewChange('node-editor')}
        className={`flex items-center gap-1 rounded-md px-3 py-1 text-sm font-bold transition-all ${
          activeView === 'node-editor'
            ? 'bg-white text-black shadow-md'
            : 'bg-transparent text-gray-400 hover:text-gray-600'
        }`}
      >
        {/* Node icon */}
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
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </svg>
        <span>Roadmap</span>
      </button>

      {/* Chart View Button */}
      <button
        onClick={() => onViewChange('chart')}
        className={`flex items-center gap-1 rounded-md px-3 py-3 text-sm font-bold transition-all ${
          activeView === 'chart'
            ? 'bg-white text-black shadow-md'
            : 'bg-transparent text-gray-400 hover:text-gray-600'
        }`}
      >
        {/* Chart icon */}
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
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        <span>Metrics</span>
      </button>
    </div>
  );
}
