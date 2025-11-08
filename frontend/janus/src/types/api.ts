/**
 * API Response Types for Backend Integration
 */

export interface DiagramNode {
  pk: number;
  title: string;
  description: string;
  next_post: number[];
}

export interface NodeMetrics {
  pk: string;
  likes: number;
  impressions: number;
  retweets: number;
}

export interface GraphResponse {
  diagram: DiagramNode[];
  metrics: NodeMetrics[];
  changes: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
