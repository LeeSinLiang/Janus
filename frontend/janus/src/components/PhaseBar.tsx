'use client';

interface Phase {
  name: string;
  dateRange: string;
  isActive?: boolean;
}

interface PhaseBarProps {
  phases: Phase[];
  onPhaseClick?: (phaseIndex: number) => void;
}

export default function PhaseBar({ phases, onPhaseClick }: PhaseBarProps) {
  return (
    <div className="flex items-center justify-center gap-48 rounded-l bg-gray-100 px-8 py-2">
      {phases.map((phase, index) => (
        <button
          key={index}
          onClick={() => onPhaseClick?.(index)}
          className={`flex flex-col items-center transition-all ${
            phase.isActive ? 'opacity-100' : 'opacity-50 hover:opacity-75'
          }`}
        >
          <span
            className={`text-sm font-semibold ${
              phase.isActive ? 'text-purple-600' : 'text-zinc-600'
            }`}
          >
            {phase.name}
          </span>
          <span
            className={`mt-0.5 text-xs ${
              phase.isActive ? 'text-purple-500' : 'text-zinc-400'
            }`}
          >
            {phase.dateRange}
          </span>
        </button>
      ))}
    </div>
  );
}
