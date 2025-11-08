'use client';

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}

function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100 text-purple-600">
        {icon}
      </div>
      <div>
        <p className="text-sm text-zinc-500">{label}</p>
        <p className="text-2xl font-bold text-zinc-900">{value}</p>
      </div>
    </div>
  );
}

interface WelcomeBarProps {
  userName?: string;
  totalPosts?: number;
  avgEngagement?: string;
  activeCampaigns?: number;
  upcomingPosts?: number;
}

export default function WelcomeBar({
  userName = 'Janus User',
  totalPosts = 124,
  avgEngagement = '21%',
  activeCampaigns = 12,
  upcomingPosts = 23,
}: WelcomeBarProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white px-8 py-6 shadow-sm">
      {/* Header */}
      <h2 className="mb-2 text-2xl font-bold text-zinc-900">
        Hi <span className="font-bold text-[#9333EA]">{userName}</span>, your campaign is live.
      </h2>
      <p className="mb-6 text-sm text-zinc-600">
        Track your real-time engagement and optimize your campaigns.
      </p>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Posts Published */}
        <StatCard
          icon={
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
          }
          label="Total Posts Published"
          value={totalPosts}
        />

        {/* Average Engagement Rate */}
        <StatCard
          icon={
            <svg
              width="24"
              height="24"
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
          }
          label="Average Engagement Rate"
          value={avgEngagement}
        />

        {/* Active Campaigns */}
        <StatCard
          icon={
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 19l7-7 3 3-7 7-3-3z" />
              <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
              <path d="M2 2l7.586 7.586" />
              <circle cx="11" cy="11" r="2" />
            </svg>
          }
          label="Active Campaigns"
          value={activeCampaigns}
        />

        {/* Upcoming Scheduled Posts */}
        <StatCard
          icon={
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          }
          label="Upcoming Scheduled Posts"
          value={upcomingPosts}
        />
      </div>
    </div>
  );
}
