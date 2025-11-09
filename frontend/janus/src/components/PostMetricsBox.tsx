'use client';

interface PostMetrics {
  pk: number;
  title: string;
  description: string;
  likes: number;
  retweets: number;
  impressions: number;
  comments: number;
}

interface PostMetricsBoxProps {
  post: PostMetrics;
}

export default function PostMetricsBox({ post }: PostMetricsBoxProps) {
  // Mock percentage changes (random between -2% and +10%)
  const getRandomPercentage = () => {
    const percentages = [
      { value: '8.6%', isPositive: true },
      { value: '8.7%', isPositive: true },
      { value: '9.7%', isPositive: true },
      { value: '7.9%', isPositive: true },
      { value: '1.3%', isPositive: false },
      { value: '6.5%', isPositive: true },
      { value: '4.2%', isPositive: true },
    ];
    return percentages[Math.floor(Math.random() * percentages.length)];
  };

  // Format numbers with K suffix (uppercase)
  const formatNumber = (num: number): string => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  // Generate mock percentages for each metric
  const replyPercentage = getRandomPercentage();
  const retweetPercentage = getRandomPercentage();
  const likePercentage = getRandomPercentage();
  const viewPercentage = getRandomPercentage();

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-3 shadow-md">
      {/* Header with X icon and title */}
      <div className="mb-2 flex items-center gap-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white flex-shrink-0">
          {/* X (Twitter) logo */}
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="black"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
        </div>
        <div className="min-w-0">
          <h3 className="text-sm font-bold text-zinc-900 truncate">{post.title}</h3>
        </div>
      </div>

      {/* Description */}
      <p className="mb-3 text-xs leading-relaxed text-zinc-500 line-clamp-2 text-center">
        {post.description}
      </p>

      {/* Metrics Grid - 2x2 */}
      <div className="space-y-2">
        {/* Row 1: Reply and Retweet */}
        <div className="flex gap-2">
          {/* Reply Metric */}
          <div className="flex-1 rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
            <div className="mb-1 flex items-center gap-1 text-[11px] font-medium text-zinc-900">
              <svg
                width="12"
                height="12"
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
            <div className="mb-1 text-2xl font-bold text-zinc-900">
              {formatNumber(post.comments)}
            </div>
            <div
              className={`flex items-center justify-center text-[11px] font-semibold ${
                replyPercentage.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              <span className="mr-0.5">
                {replyPercentage.isPositive ? '↑' : '↓'}
              </span>
              <span className="truncate">{replyPercentage.value}</span>
            </div>
          </div>

          {/* Retweet Metric */}
          <div className="flex-1 rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
            <div className="mb-1 flex items-center gap-1 text-[11px] font-medium text-zinc-900">
              <svg
                width="12"
                height="12"
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
            <div className="mb-1 text-2xl font-bold text-zinc-900">
              {formatNumber(post.retweets)}
            </div>
            <div
              className={`flex items-center justify-center text-[11px] font-semibold ${
                retweetPercentage.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              <span className="mr-0.5">
                {retweetPercentage.isPositive ? '↑' : '↓'}
              </span>
              <span className="truncate">{retweetPercentage.value}</span>
            </div>
          </div>
        </div>

        {/* Row 2: Like and View */}
        <div className="flex gap-2">
          {/* Like Metric */}
          <div className="flex-1 rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
            <div className="mb-1 flex items-center gap-1 text-[11px] font-medium text-zinc-900">
              <svg
                width="12"
                height="12"
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
            <div className="mb-1 text-2xl font-bold text-zinc-900">
              {formatNumber(post.likes)}
            </div>
            <div
              className={`flex items-center justify-center text-[11px] font-semibold ${
                likePercentage.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              <span className="mr-0.5">
                {likePercentage.isPositive ? '↑' : '↓'}
              </span>
              <span className="truncate">{likePercentage.value}</span>
            </div>
          </div>

          {/* View Metric */}
          <div className="flex-1 rounded-lg border-2 border-purple-300 bg-white p-2 flex flex-col items-center justify-center">
            <div className="mb-1 flex items-center gap-1 text-[11px] font-medium text-zinc-900">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <span>View</span>
            </div>
            <div className="mb-1 text-2xl font-bold text-zinc-900">
              {formatNumber(post.impressions)}
            </div>
            <div
              className={`flex items-center justify-center text-[11px] font-semibold ${
                viewPercentage.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              <span className="mr-0.5">
                {viewPercentage.isPositive ? '↑' : '↓'}
              </span>
              <span className="truncate">{viewPercentage.value}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
