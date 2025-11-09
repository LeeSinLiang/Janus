'use client';

import { useEffect } from 'react';

interface TriggerNotificationProps {
  triggeredPosts: Array<{
    post_pk: number;
    post_title: string;
    trigger_condition: string;
    trigger_value: number;
    trigger_comparison: string;
    current_value_a: number;
    current_value_b: number;
    triggered_variants: string[];
    elapsed_time_seconds: number;
    trigger_prompt: string;
  }>;
  count: number;
  status: 'triggering' | 'completed';
  onDismiss: () => void;
  autoDismissDelay?: number;
}

export default function TriggerNotification({
  triggeredPosts,
  count,
  status,
  onDismiss,
  autoDismissDelay = 10000, // Auto-dismiss after 10 seconds
}: TriggerNotificationProps) {
  // Auto-dismiss after specified delay
  useEffect(() => {
    if (autoDismissDelay > 0) {
      const timer = setTimeout(onDismiss, autoDismissDelay);
      return () => clearTimeout(timer);
    }
  }, [autoDismissDelay, onDismiss]);

  // Theme colors based on status
  const themeConfig = status === 'completed' ? {
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    dotColor: 'bg-green-500',
    textColor: 'text-green-700',
    lightTextColor: 'text-green-500',
    darkTextColor: 'text-green-900',
    itemBg: 'bg-white/70',
    itemBorder: 'border-green-100',
    footerTextColor: 'text-green-600',
    footerBorderColor: 'border-green-100',
    closeColor: 'text-green-600 hover:text-green-800',
  } : {
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    dotColor: 'bg-orange-500',
    textColor: 'text-orange-700',
    lightTextColor: 'text-orange-500',
    darkTextColor: 'text-orange-900',
    itemBg: 'bg-white/70',
    itemBorder: 'border-orange-100',
    footerTextColor: 'text-orange-600',
    footerBorderColor: 'border-orange-100',
    closeColor: 'text-orange-600 hover:text-orange-800',
  };

  return (
    <div
      className="
        fixed top-6 right-6 z-50 w-96
        animate-in slide-in-from-right duration-300
      "
    >
      <div
        className={`
          flex flex-col gap-3 px-5 py-4 rounded-xl border backdrop-blur-sm
          ${themeConfig.bgColor} ${themeConfig.borderColor}
          shadow-lg transition-all duration-200
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Dot indicator (pulsing for triggering, static for completed) */}
            <div className="flex items-center">
              <div className={`relative h-2.5 w-2.5 rounded-full ${themeConfig.dotColor}`}>
                {status === 'triggering' && (
                  <>
                    <div className={`absolute inset-0 rounded-full ${themeConfig.dotColor} animate-ping opacity-75`} />
                    <div className={`absolute inset-0 rounded-full ${themeConfig.dotColor}`} />
                  </>
                )}
              </div>
            </div>

            {/* Title */}
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold ${themeConfig.textColor}`}>
                {status === 'completed' ? 'Regeneration Complete!' : 'Trigger Fired'}
              </span>
              <span className="text-xs text-zinc-500">
                {count} {count === 1 ? 'post' : 'posts'} {status === 'completed' ? 'ready for review' : 'regenerating'}
              </span>
            </div>

            {/* Icon: Spinner for triggering, Checkmark for completed */}
            <div>
              {status === 'triggering' ? (
                <svg
                  className={`animate-spin h-4 w-4 ${themeConfig.textColor}`}
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
              ) : (
                <svg
                  className={`h-4 w-4 ${themeConfig.textColor}`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="3"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              )}
            </div>
          </div>

          {/* Close button */}
          <button
            onClick={onDismiss}
            className={`${themeConfig.closeColor} transition-colors`}
            title="Dismiss"
          >
            <svg
              width="16"
              height="16"
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

        {/* Triggered posts list */}
        <div className="flex flex-col gap-2 max-h-60 overflow-y-auto">
          {triggeredPosts.map((post, index) => (
            <div
              key={post.post_pk}
              className={`
                px-3 py-2 rounded-lg
                ${themeConfig.itemBg} border ${themeConfig.itemBorder}
                text-xs
              `}
            >
              <div className={`font-medium ${themeConfig.darkTextColor} mb-1`}>
                {post.post_title}
              </div>
              <div className={`${themeConfig.textColor} flex items-center gap-2`}>
                <span className="font-mono">
                  {post.trigger_condition} {post.trigger_comparison} {post.trigger_value}
                </span>
                <span className={themeConfig.lightTextColor}>•</span>
                <span>
                  Variants: {post.triggered_variants.join(', ')}
                </span>
              </div>
              {post.trigger_prompt && (
                <div className="mt-1 text-zinc-600 italic">
                  "{post.trigger_prompt}"
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Footer message */}
        <div className={`text-xs ${themeConfig.footerTextColor} border-t ${themeConfig.footerBorderColor} pt-2`}>
          {status === 'completed'
            ? 'Assets ready! Posts moved to draft for your review.'
            : 'Content regeneration started in background. Posts will move to draft for review.'}
        </div>
      </div>
    </div>
  );
}
