/**
 * API Response Types for Backend Integration
 */

export interface NodeMetrics {
  node_id: string;
  likes: number;
  impressions: number;
  retweets: number;
}

export interface GraphResponse {
  diagram: string;
  metrics: NodeMetrics[];
  changes: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
