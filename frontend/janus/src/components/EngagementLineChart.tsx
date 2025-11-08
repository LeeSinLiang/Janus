'use client';

interface DataPoint {
  date: string;
  likes: number;
  comments: number;
  impressions: number;
}

interface EngagementLineChartProps {
  data?: DataPoint[];
}

export default function EngagementLineChart({ data }: EngagementLineChartProps) {
  // Default sample data
  const defaultData: DataPoint[] = [
    { date: 'Nov 1', likes: 800, comments: 600, impressions: 400 },
    { date: 'Nov 2', likes: 1800, comments: 1400, impressions: 900 },
    { date: 'Nov 3', likes: 1200, comments: 900, impressions: 700 },
    { date: 'Nov 4', likes: 3400, comments: 2800, impressions: 2200 },
    { date: 'Nov 5', likes: 2800, comments: 2200, impressions: 1800 },
    { date: 'Nov 6', likes: 4800, comments: 3800, impressions: 3000 },
    { date: 'Nov 7', likes: 5200, comments: 4000, impressions: 3200 },
  ];

  const chartData = data || defaultData;

  // Find max value for scaling
  const maxValue = Math.max(
    ...chartData.flatMap(d => [d.likes, d.comments, d.impressions])
  );
  const roundedMax = Math.ceil(maxValue / 1000) * 1000;

  // Generate Y-axis labels
  const yLabels = [0, 1000, 2000, 3000, 4000, 5000];

  // Calculate SVG path for a line
  const createPath = (dataKey: 'likes' | 'comments' | 'impressions') => {
    const points = chartData.map((d, i) => {
      const x = (i / (chartData.length - 1)) * 100;
      const y = 100 - (d[dataKey] / roundedMax) * 100;
      return `${x},${y}`;
    });
    return `M ${points.join(' L ')}`;
  };

  return (
    <div className="rounded-xl border border-zinc-200 bg-white px-8 py-6 shadow-sm">
      <h3 className="mb-2 text-lg font-semibold text-zinc-900">
        Post Engagement Trend
      </h3>
      <p className="mb-6 text-sm text-zinc-500">
        Likes & Comments Growth (Last 7 Days)
      </p>

      {/* Chart */}
      <div className="relative">
        {/* Y-axis labels */}
        <div className="absolute -left-2 top-0 flex h-full flex-col justify-between text-xs text-zinc-500">
          {yLabels.reverse().map((label) => (
            <div key={label}>{(label / 1000).toFixed(1)}K</div>
          ))}
        </div>

        {/* SVG Chart */}
        <div className="ml-12">
          <svg
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            className="h-64 w-full"
          >
            {/* Grid lines */}
            {[0, 20, 40, 60, 80, 100].map((y) => (
              <line
                key={y}
                x1="0"
                y1={y}
                x2="100"
                y2={y}
                stroke="#f1f5f9"
                strokeWidth="0.2"
              />
            ))}

            {/* Impressions line (lightest) */}
            <path
              d={createPath('impressions')}
              fill="none"
              stroke="#c084fc"
              strokeWidth="0.5"
              vectorEffect="non-scaling-stroke"
            />

            {/* Comments line (medium) */}
            <path
              d={createPath('comments')}
              fill="none"
              stroke="#a855f7"
              strokeWidth="0.5"
              vectorEffect="non-scaling-stroke"
            />

            {/* Likes line (darkest) */}
            <path
              d={createPath('likes')}
              fill="none"
              stroke="#7c3aed"
              strokeWidth="0.5"
              vectorEffect="non-scaling-stroke"
            />
          </svg>

          {/* X-axis labels */}
          <div className="mt-2 flex justify-between text-xs text-zinc-500">
            {chartData.map((d) => (
              <div key={d.date}>{d.date}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
