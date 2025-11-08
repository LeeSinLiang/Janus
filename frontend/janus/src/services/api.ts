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

  // Return mock data matching sample_response.json
  return {
    diagram: `graph TB
    subgraph "Phase 1"
        NODE1[<title>Instagram post</title><description>Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post</description><variant1_title>Feature-focused</variant1_title><variant1_description>Feature-focused version...</variant1_description><variant2_title>Emotion-focused</variant2_title><variant2_description>Emotion-focused version ...</variant2_description>]
        NODE2[<title>X post</title><description>Create an Instagram carousel post (5 slides) highlighting our top features.</description>]
        NODE3[<title>Instagram Reels</title><description>Create an Instagram carousel post (5 slides) highlighting our top features.</description>]
    end

    subgraph "Phase 2"
        NODE4[<title>Youtube Shorts</title><description>Create an Instagram carousel post (5 slides) highlighting our top features.</description>]
        NODE5[<title>Video Marketing</title><description>Create an Instagram carousel post (5 slides) highlighting our top features.</description>]
    end



    NODE1 --> NODE2
    NODE1 --> NODE3
    NODE2 --> NODE4
    NODE3 --> NODE5
    NODE4 --> NODE5
    NODE2 --> NODE3
`,
    metrics: [
      { node_id: 'NODE1', likes: 124, impressions: 1570, retweets: 45 },
      { node_id: 'NODE2', likes: 98, impressions: 2034, retweets: 67 },
      { node_id: 'NODE3', likes: 215, impressions: 3098, retweets: 120 },
      { node_id: 'NODE4', likes: 56, impressions: 890, retweets: 10 },
      { node_id: 'NODE5', likes: 180, impressions: 2500, retweets: 85 },
    ],
    changes: false,
  };
}
