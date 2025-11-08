'use client';

interface EngagementData {
  likes: number;
  comments: number;
  shares: number;
}

interface EngagementPieChartProps {
  data?: EngagementData;
}

export default function EngagementPieChart({ data }: EngagementPieChartProps) {
  // Default sample data
  const defaultData: EngagementData = {
    likes: 45,
    comments: 35,
    shares: 20,
  };

  const chartData = data || defaultData;
  const total = chartData.likes + chartData.comments + chartData.shares;

  // Calculate percentages
  const likesPercent = (chartData.likes / total) * 100;
  const commentsPercent = (chartData.comments / total) * 100;
  const sharesPercent = (chartData.shares / total) * 100;

  // Calculate angles for pie chart (SVG uses degrees starting from top)
  const likesAngle = (likesPercent / 100) * 360;
  const commentsAngle = (commentsPercent / 100) * 360;
  const sharesAngle = (sharesPercent / 100) * 360;

  // Helper to create arc path
  const createArc = (
    startAngle: number,
    endAngle: number,
    radius: number = 40,
    innerRadius: number = 25
  ) => {
    const start = polarToCartesian(50, 50, radius, startAngle);
    const end = polarToCartesian(50, 50, radius, endAngle);
    const innerStart = polarToCartesian(50, 50, innerRadius, startAngle);
    const innerEnd = polarToCartesian(50, 50, innerRadius, endAngle);
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;

    return [
      `M ${start.x} ${start.y}`,
      `A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y}`,
      `L ${innerEnd.x} ${innerEnd.y}`,
      `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${innerStart.x} ${innerStart.y}`,
      'Z',
    ].join(' ');
  };

  function polarToCartesian(
    centerX: number,
    centerY: number,
    radius: number,
    angleInDegrees: number
  ) {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians),
    };
  }

  // Calculate cumulative angles
  let currentAngle = 0;
  const likesStart = currentAngle;
  const likesEnd = currentAngle + likesAngle;
  currentAngle = likesEnd;

  const commentsStart = currentAngle;
  const commentsEnd = currentAngle + commentsAngle;
  currentAngle = commentsEnd;

  const sharesStart = currentAngle;
  const sharesEnd = currentAngle + sharesAngle;

  return (
    <div className="rounded-xl border border-zinc-200 bg-white px-8 py-6 shadow-sm">
      <h3 className="mb-2 text-lg font-semibold text-zinc-900">
        Post Engagement Trend
      </h3>
      <p className="mb-6 text-sm text-zinc-500">Engagement Breakdown (Bar Chart)</p>

      {/* Chart Container */}
      <div className="flex items-center justify-center">
        <div className="relative">
          <svg width="300" height="300" viewBox="0 0 100 100">
            {/* Likes segment (darkest purple) */}
            <path
              d={createArc(likesStart, likesEnd)}
              fill="#7c3aed"
            />

            {/* Comments segment (medium purple) */}
            <path
              d={createArc(commentsStart, commentsEnd)}
              fill="#a855f7"
            />

            {/* Shares segment (light purple) */}
            <path
              d={createArc(sharesStart, sharesEnd)}
              fill="#c084fc"
            />

            {/* Center white circle */}
            <circle cx="50" cy="50" r="25" fill="white" />
          </svg>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-8 flex justify-center gap-8">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-[#7c3aed]"></div>
          <span className="text-sm text-zinc-700">Likes</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-[#a855f7]"></div>
          <span className="text-sm text-zinc-700">Comments</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-[#c084fc]"></div>
          <span className="text-sm text-zinc-700">Shares</span>
        </div>
      </div>
    </div>
  );
}
