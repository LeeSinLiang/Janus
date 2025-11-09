/**
 * API Response Types for Backend Integration
 */

export interface DiagramNode {
  pk: number;
  title: string;
  description: string;
  next_posts: number[];
  phase: string;
  status?: string; // draft, published, etc.
}

export interface NodeMetrics {
  likes: number;
  impressions: number;
  retweets: number;
}

export interface CampaignInfo {
  campaign_id: string;
  name: string;
  phase: 'planning' | 'content_creation' | 'scheduled' | 'active' | 'analyzing' | 'completed';
  description: string;
}

export interface GraphResponse {
  diagram: DiagramNode[];
  metrics: Record<number, NodeMetrics>; // Object with pk as key
  changes: boolean;
  campaign?: CampaignInfo | null;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
