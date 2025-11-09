'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchCampaigns } from '@/services/api';
import { Campaign } from '@/types/api';

export default function CampaignList() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCampaigns = async () => {
      try {
        setIsLoading(true);
        const response = await fetchCampaigns();
        setCampaigns(response.campaigns);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch campaigns:', err);
        setError('Failed to load campaigns');
      } finally {
        setIsLoading(false);
      }
    };

    loadCampaigns();
  }, []);

  const handleCampaignClick = (campaignId: string) => {
    router.push(`/canvas?campaign_id=${campaignId}`);
  };

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'planning':
        return 'bg-blue-100 text-blue-700';
      case 'content_creation':
        return 'bg-yellow-100 text-yellow-700';
      case 'scheduled':
        return 'bg-purple-100 text-purple-700';
      case 'active':
        return 'bg-green-100 text-green-700';
      case 'analyzing':
        return 'bg-indigo-100 text-indigo-700';
      case 'completed':
        return 'bg-gray-100 text-gray-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mt-8">
        <div className="text-center text-gray-500">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="mt-2 text-sm">Loading campaigns...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mt-8">
        <div className="text-center text-red-500 text-sm">{error}</div>
      </div>
    );
  }

  if (campaigns.length === 0) {
    return null; // Don't show anything if no campaigns exist
  }

  return (
    <div className="w-full max-w-4xl mt-8">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-700">Previous Campaigns</h3>
        <p className="text-sm text-gray-500">Click on a campaign to view details</p>
      </div>

      <div className="space-y-3 max-h-64 overflow-y-auto">
        {campaigns.map((campaign) => (
          <button
            key={campaign.campaign_id}
            onClick={() => handleCampaignClick(campaign.campaign_id)}
            className="w-full bg-white rounded-lg border border-gray-200 shadow-sm px-6 py-4 text-left transition-all hover:border-orange-400 hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-semibold text-gray-900">{campaign.name}</h4>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getPhaseColor(
                      campaign.phase
                    )}`}
                  >
                    {campaign.phase.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                  {campaign.description}
                </p>
                <p className="text-xs text-gray-400">
                  Created {formatDate(campaign.created_at)}
                </p>
              </div>

              <svg
                className="w-5 h-5 text-gray-400 ml-4 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
