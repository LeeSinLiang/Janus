import { GraphResponse, ApiError } from '@/types/api';

// Configure your API endpoint here
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GRAPH_ENDPOINT = '/api/graph';

/**
 * Fetch graph data from the backend
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
 * Approve a node - sends POST request with node name
 */
export async function approveNode(nodeName: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ node_name: nodeName }),
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
 * Reject a node - sends POST request with node name and rejection message
 */
export async function rejectNode(nodeName: string, rejectMessage: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}${GRAPH_ENDPOINT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        node_name: nodeName,
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
 * Mock function for development/testing
 * Remove this when connecting to real backend
 */
export async function fetchGraphDataMock(): Promise<GraphResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Return mock data matching new JSON format
  return {
    diagram: [
      {
        pk: 1,
        title: 'Instagram post',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post.',
        next_post: [2, 3],
      },
      {
        pk: 2,
        title: 'X post',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_post: [4, 3],
      },
      {
        pk: 3,
        title: 'Instagram Reels',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_post: [5],
      },
      {
        pk: 4,
        title: 'Youtube Shorts',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_post: [5],
      },
      {
        pk: 5,
        title: 'Video Marketing',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        next_post: [],
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
