'use client';

interface VariantMetrics {
  likes: number;
  retweets: number;
  comments: number;
  positivity: number; // Percentage (0-100)
}

interface VariantMetricsBoxProps {
  metrics: VariantMetrics;
}

export default function VariantMetricsBox({ metrics }: VariantMetricsBoxProps) {
  // Format numbers with K suffix
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="grid grid-cols-2 gap-2 mt-4">
      {/* Like Metric */}
      <div className="rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
        <div className="mb-1 flex items-center gap-1 text-[10px] font-medium text-zinc-900">
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
          <span>Like</span>
        </div>
        <div className="text-xl font-bold text-zinc-900">
          {formatNumber(metrics.likes)}
        </div>
      </div>

      {/* Retweet Metric */}
      <div className="rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
        <div className="mb-1 flex items-center gap-1 text-[10px] font-medium text-zinc-900">
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 0 1 4-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 0 1-4 4H3" />
          </svg>
          <span>Retweet</span>
        </div>
        <div className="text-xl font-bold text-zinc-900">
          {formatNumber(metrics.retweets)}
        </div>
      </div>

      {/* Comment Metric */}
      <div className="rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
        <div className="mb-1 flex items-center gap-1 text-[10px] font-medium text-zinc-900">
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
          </svg>
          <span>Reply</span>
        </div>
        <div className="text-xl font-bold text-zinc-900">
          {formatNumber(metrics.comments)}
        </div>
      </div>

      {/* Comment Positivity Metric */}
      <div className="rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
        <div className="mb-1 flex items-center gap-1 text-[10px] font-medium text-zinc-900">
          <svg
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M8 14s1.5 2 4 2 4-2 4-2" />
            <line x1="9" y1="9" x2="9.01" y2="9" />
            <line x1="15" y1="9" x2="15.01" y2="9" />
          </svg>
          <span>Positive</span>
        </div>
        <div className="text-xl font-bold text-zinc-900">
          {metrics.positivity}%
        </div>
      </div>
    </div>
  );
}
