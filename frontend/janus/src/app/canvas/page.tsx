'use client';

import { useSearchParams } from 'next/navigation';
import CanvasWithPolling from "@/components/CanvasWithPolling";

export default function CanvasPage() {
  const searchParams = useSearchParams();
  const campaignId = searchParams.get('campaign_id');

  return (
    <div className="h-screen w-screen">
      <CanvasWithPolling campaignId={campaignId || undefined} />
    </div>
  );
}
