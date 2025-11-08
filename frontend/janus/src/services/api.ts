import { DiagramNode, GraphResponse, ApiError } from '@/types/api';

// Configure your API endpoint here
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GRAPH_ENDPOINT = '/api/graph';

/**
 * Fetch graph data from the backend (Version 1)
 * Expects plain Post[] array from /nodesJson/
 */
export async function fetchGraphDataV1(): Promise<DiagramNode[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/nodesJson/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add credentials if needed for authentication
      // credentials: 'include',
    });

    if (!response.ok) {
      const error: ApiError = {
        message: `API request failed: ${response.statusText}`,
        status: response.status,
      };
      throw error;
    }

    const data: DiagramNode[] = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching graph data V1:', error);
    throw error;
  }
}

/**
 * Fetch graph data from the backend (Version 2)
 * Expects enriched format with diagram, metrics, and changes from /nodesJson/
 */
export async function fetchGraphDataV2(): Promise<GraphResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/nodesJson/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add credentials if needed for authentication
      // credentials: 'include',
    });

    if (!response.ok) {
      const error: ApiError = {
        message: `API request failed: ${response.statusText}`,
        status: response.status,
      };
      throw error;
    }

    const data: GraphResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching graph data V2:', error);
    throw error;
  }
}

/**
 * Fetch graph data from the backend (Legacy)
 * @deprecated Use fetchGraphDataV1() or fetchGraphDataV2() instead
 */
export async function fetchGraphData(): Promise<GraphResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}${GRAPH_ENDPOINT}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add credentials if needed for authentication
      // credentials: 'include',
    });

    if (!response.ok) {
      const error: ApiError = {
        message: `API request failed: ${response.statusText}`,
        status: response.status,
      };
      throw error;
    }

    const data: GraphResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  }
}

/**
 * Approve a node - sends POST request with node pk
 */
export async function approveNode(nodePk: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk: nodePk }),
    });

    if (!response.ok) {
      throw new Error(`Failed to approve node: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error approving node:', error);
    throw error;
  }
}

/**
 * Create X post from a node - sends POST request with node pk
 */
export async function createXPost(nodePk: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/createXPost/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk: nodePk }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create X post: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating X post:', error);
    throw error;
  }
}

/**
 * Reject a node - sends POST request with node pk and rejection message
 */
export async function rejectNode(nodePk: string, rejectMessage: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}${GRAPH_ENDPOINT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pk: nodePk,
        reject_message: rejectMessage
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to reject node: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error rejecting node:', error);
    throw error;
  }
}

/**
 * Fetch content variants for a post by pk
 */
export async function fetchVariants(pk: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/getVariants/?pk=${pk}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch variants: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching variants:', error);
    throw error;
  }
}

/**
 * Save selected variant for a post
 */
export async function selectVariant(pk: string, variantId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/selectVariant/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk, variant_id: variantId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to select variant: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error selecting variant:', error);
    throw error;
  }
}

/**
 * Mock function for development/testing
 * Remove this when connecting to real backend
 */
export async function fetchGraphDataMock(): Promise<GraphResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Return mock data matching backend format with next_posts (plural) and phase
  return {
    diagram: [
      {
        pk: 1,
        title: 'Instagram post',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post.',
        next_posts: [2],
        phase: 'Phase 1',
      },
      {
        pk: 2,
        title: 'X post',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_posts: [3],
        phase: 'Phase 1',
      },
      {
        pk: 3,
        title: 'Instagram Reels',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_posts: [],
        phase: 'Phase 2',
      },
      {
        pk: 4,
        title: 'Youtube Shorts',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_posts: [2, 5],
        phase: 'Phase 2',
      },
      {
        pk: 5,
        title: 'Video Marketing',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_posts: [],
        phase: 'Phase 3',
      },
    ],
    metrics: [
      { pk: '1', likes: 124, impressions: 1570, retweets: 45 },
      { pk: '2', likes: 98, impressions: 2034, retweets: 67 },
      { pk: '3', likes: 215, impressions: 3098, retweets: 120 },
      { pk: '4', likes: 56, impressions: 890, retweets: 10 },
      { pk: '5', likes: 180, impressions: 2500, retweets: 85 },
    ],
    changes: false,
  };
}
