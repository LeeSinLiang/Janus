import { DiagramNode, GraphResponse, ApiError, CampaignsResponse } from '@/types/api';

// Configure your API endpoint here
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GRAPH_ENDPOINT = '/api/graph';

/**
 * Fetch graph data from the backend (Version 1)
 * Expects { diagram: Post[], metrics: Record<string, NodeMetrics> } from /nodesJson/
 */
export async function fetchGraphDataV1(campaignId?: string): Promise<GraphResponse> {
  try {
    // Build URL with optional campaign_id query param
    const url = new URL(`${API_BASE_URL}/nodesJson/`);
    if (campaignId) {
      url.searchParams.append('campaign_id', campaignId);
    }

    const response = await fetch(url.toString(), {
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

    const data = await response.json();

    // Convert metrics object keys from strings to numbers
    const metricsWithNumberKeys: Record<number, any> = {};
    if (data.metrics && typeof data.metrics === 'object') {
      Object.keys(data.metrics).forEach(key => {
        metricsWithNumberKeys[Number(key)] = data.metrics[key];
      });
    }

    return {
      diagram: data.diagram || [],
      metrics: metricsWithNumberKeys,
      post_metrics: data.post_metrics || [],
      campaign: data.campaign || null,
      changes: true, // Always process on fetch
    };
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
 * Approve all draft nodes in a campaign - sends POST request with campaign_id
 */
export async function approveAllNodes(campaignId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/approveAll`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ campaign_id: campaignId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to approve all nodes: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error approving all nodes:', error);
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
 * Get X post metrics for a node - sends POST request with node pk
 * Updates the post metrics in the database
 */
export async function getXPostMetrics(nodePk: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/getXPostMetrics/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk: nodePk }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get X post metrics: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting X post metrics:', error);
    throw error;
  }
}

/**
 * Generate a marketing strategy - sends POST request with product description and GTM goals
 */
export async function generateStrategy(params: {
  product_description: string;
  gtm_goals: string;
  campaign_name: string;
}): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agents/strategy/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate strategy: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating strategy:', error);
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
 * Send trigger for a node - sends POST request with node pk and trigger type
 * @deprecated Use parseTrigger instead
 */
export async function sendTrigger(pk: number, trigger: 'like' | 'retweet'): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/setTrigger/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk, trigger }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send trigger: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error sending trigger:', error);
    throw error;
  }
}

/**
 * Parse natural language trigger prompt and save to post
 * New robust trigger mechanism using TriggerParserAgent
 */
export async function parseTrigger(
  pk: number,
  condition: 'likes' | 'retweets' | 'impressions' | 'comments',
  prompt: string
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/parseTrigger/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pk, condition, prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to parse trigger: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error parsing trigger:', error);
    throw error;
  }
}

/**
 * Fetch list of all campaigns
 */
export async function fetchCampaigns(): Promise<CampaignsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agents/campaigns/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch campaigns: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    throw error;
  }
}

/**
 * Check triggers - sends GET request to check if any triggers should fire
 */
export async function checkTrigger(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/checkTrigger/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    // Silent check - no error handling needed
  } catch (error) {
    // Silently fail - this is a background check
  }
}

/**
 * Send multi-node prompt - sends POST request with selected node pks and user prompt
 * Generates a new post based on selected posts
 */
export async function sendMultiNodePrompt(nodes: number[], prompt: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/agents/generate-new-post/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ nodes, prompt }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send multi-node prompt: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending multi-node prompt:', error);
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
    metrics: {
      1: { likes: 124, impressions: 1570, retweets: 45 },
      2: { likes: 98, impressions: 2034, retweets: 67 },
      3: { likes: 215, impressions: 3098, retweets: 120 },
      4: { likes: 56, impressions: 890, retweets: 10 },
      5: { likes: 180, impressions: 2500, retweets: 85 },
    },
    post_metrics: [
      {
        pk: 1,
        title: 'X post 1',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        likes: 34700,
        retweets: 8300,
        impressions: 54600,
        comments: 22400,
      },
      {
        pk: 2,
        title: 'X post 2',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        likes: 34700,
        retweets: 8300,
        impressions: 34600,
        comments: 22400,
      },
      {
        pk: 3,
        title: 'X post 3',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        likes: 34700,
        retweets: 8300,
        impressions: 34600,
        comments: 22400,
      },
      {
        pk: 4,
        title: 'X post 4',
        description: 'Create an Instagram carousel post (5 slides) highlighting our top features.',
        likes: 34700,
        retweets: 8300,
        impressions: 54600,
        comments: 22400,
      },
    ],
    campaign: {
      campaign_id: 'mock_campaign_1',
      name: 'Mock Campaign',
      phase: 'planning',
      description: 'Mock campaign for testing',
    },
    changes: false,
  };
}
