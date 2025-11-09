'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import CanvasWithPolling from "@/components/CanvasWithPolling";

function CanvasContent() {
  const searchParams = useSearchParams();
  const campaignId = searchParams.get('campaign_id');

  return (
    <div className="h-screen w-screen">
      <CanvasWithPolling campaignId={campaignId || undefined} />
    </div>
  );
}

export default function CanvasPage() {
  return (
    <Suspense fallback={<div className="h-screen w-screen flex items-center justify-center">Loading...</div>}>
      <CanvasContent />
    </Suspense>
  );
}
