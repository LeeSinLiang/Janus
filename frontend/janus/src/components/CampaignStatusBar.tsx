'use client';

import { CampaignInfo } from '@/types/api';

interface CampaignStatusBarProps {
  campaign: CampaignInfo | null;
}

// Status configuration with colors and labels
const STATUS_CONFIG: Record<
  CampaignInfo['phase'],
  {
    label: string;
    description: string;
    bgColor: string;
    textColor: string;
    borderColor: string;
    dotColor: string;
  }
> = {
  planning: {
    label: 'Planning',
    description: 'Strategy being developed',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    borderColor: 'border-blue-200',
    dotColor: 'bg-blue-500',
  },
  content_creation: {
    label: 'Generating Content',
    description: 'AI creating variants',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-700',
    borderColor: 'border-purple-200',
    dotColor: 'bg-purple-500',
  },
  scheduled: {
    label: 'Scheduled',
    description: 'Ready to launch',
    bgColor: 'bg-cyan-50',
    textColor: 'text-cyan-700',
    borderColor: 'border-cyan-200',
    dotColor: 'bg-cyan-500',
  },
  active: {
    label: 'Active',
    description: 'Campaign running',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    borderColor: 'border-green-200',
    dotColor: 'bg-green-500',
  },
  analyzing: {
    label: 'Analyzing',
    description: 'Processing metrics',
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-700',
    borderColor: 'border-amber-200',
    dotColor: 'bg-amber-500',
  },
  completed: {
    label: 'Completed',
    description: 'Campaign finished',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-700',
    borderColor: 'border-gray-200',
    dotColor: 'bg-gray-500',
  },
};

export default function CampaignStatusBar({ campaign }: CampaignStatusBarProps) {
  if (!campaign) {
    return null;
  }

  const config = STATUS_CONFIG[campaign.phase];

  if (!config) {
    return null;
  }

  const isProcessing = campaign.phase === 'planning' || campaign.phase === 'content_creation';

  return (
    <div
      className={`
        flex items-center gap-3 px-5 py-2.5 rounded-xl border backdrop-blur-sm
        ${config.bgColor} ${config.borderColor}
        shadow-sm transition-all duration-200
      `}
    >
      {/* Status Indicator Dot with pulse animation for active states */}
      <div className="flex items-center">
        <div className={`relative h-2.5 w-2.5 rounded-full ${config.dotColor}`}>
          {(isProcessing || campaign.phase === 'active') && (
            <>
              <div className={`absolute inset-0 rounded-full ${config.dotColor} animate-ping opacity-75`} />
              <div className={`absolute inset-0 rounded-full ${config.dotColor}`} />
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex items-center gap-3">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${config.textColor}`}>
              {config.label}
            </span>
            <span className="text-xs text-zinc-500">
              {config.description}
            </span>
          </div>
          {campaign.name && campaign.name !== campaign.campaign_id && (
            <span className="text-xs text-zinc-400 font-medium">
              {campaign.name}
            </span>
          )}
        </div>

        {/* Loading indicator for planning and content_creation phases */}
        {isProcessing && (
          <div className="ml-1">
            <svg
              className={`animate-spin h-4 w-4 ${config.textColor}`}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
