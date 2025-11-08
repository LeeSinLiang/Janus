/**
 * Test helper for the approval system
 *
 * Use this to toggle between having 5 nodes and 6 nodes to test
 * the approval flow without modifying the main mock data.
 */

let showExtraNode = false;

export function toggleTestNode() {
  showExtraNode = !showExtraNode;
  console.log(`Test node ${showExtraNode ? 'enabled' : 'disabled'}`);
  return showExtraNode;
}

export function getTestDiagram(): string {
  const baseDiagram = `graph TB
    subgraph "Phase 1"
        NODE1[<title>Instagram post</title><description>Create an Instagram carousel post (5 slides) highlighting our top features. Create an Instagram carousel post</description>]
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
    NODE4 <--> NODE5
    NODE2 <--> NODE3`;

  const extraNode = `

    subgraph "Phase 3"
        NODE6[<title>LinkedIn Post</title><description>Share company updates and engage with professional network. Post should highlight recent achievements.</description>]
    end

    NODE5 --> NODE6`;

  return showExtraNode ? baseDiagram + extraNode : baseDiagram;
}

export function getTestMetrics() {
  const baseMetrics = [
    { node_id: 'NODE1', likes: 124, impressions: 1570, retweets: 45 },
    { node_id: 'NODE2', likes: 98, impressions: 2034, retweets: 67 },
    { node_id: 'NODE3', likes: 215, impressions: 3098, retweets: 120 },
    { node_id: 'NODE4', likes: 56, impressions: 890, retweets: 10 },
    { node_id: 'NODE5', likes: 180, impressions: 2500, retweets: 85 },
  ];

  const extraMetric = { node_id: 'NODE6', likes: 0, impressions: 0, retweets: 0 };

  return showExtraNode ? [...baseMetrics, extraMetric] : baseMetrics;
}

export function hasTestChanges(): boolean {
  return showExtraNode;
}

/**
 * Instructions for testing:
 *
 * 1. In your browser console, run:
 *    window.toggleTestNode = require('./services/testApproval').toggleTestNode
 *
 * 2. Call window.toggleTestNode() to add NODE6
 *
 * 3. Wait 5 seconds for the next poll
 *
 * 4. NODE6 should appear with green border and approve/reject buttons
 *
 * 5. Click approve or reject to test functionality
 *
 * 6. Call window.toggleTestNode() again to remove NODE6 (or add it back)
 */
