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
  has_trigger?: boolean;
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

export interface PostMetrics {
  pk: number;
  title: string;
  description: string;
  likes: number;
  retweets: number;
  impressions: number;
  comments: number;
}

export interface GraphResponse {
  diagram: DiagramNode[];
  metrics: Record<number, NodeMetrics>; // Object with pk as key
  post_metrics?: PostMetrics[]; // First 4 published posts with metrics
  changes: boolean;
  campaign?: CampaignInfo | null;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}

export interface Variant {
  variant_id: string;
  content: string;
  platform: string;
  asset?: string;
  metadata: {
    hook?: string;
    reasoning?: string;
    hashtags?: string[];
  };
}

export interface Campaign {
  id: number;
  campaign_id: string;
  name: string;
  description: string;
  phase: 'planning' | 'content_creation' | 'scheduled' | 'active' | 'analyzing' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface CampaignsResponse {
  success: boolean;
  count: number;
  campaigns: Campaign[];
}
