'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Node, Edge } from '@xyflow/react';
import { fetchGraphData, fetchGraphDataMock, fetchGraphDataV1, fetchGraphDataV2 } from '@/services/api';
import { parseGraphData } from '@/utils/graphParser';
import { diffGraphData, applyGraphDiff } from '@/utils/graphDiff';

interface UseGraphDataOptions {
  pollingInterval?: number; // in milliseconds
  useMockData?: boolean; // for development/testing
}

interface UseGraphDataReturn {
  nodes: Node[];
  edges: Edge[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  setNodes: React.Dispatch<React.SetStateAction<Node[]>>;
  setEdges: React.Dispatch<React.SetStateAction<Edge[]>>;
}

/**
 * Custom hook for fetching and managing graph data with automatic polling
 *
 * @param options - Configuration options
 * @param options.pollingInterval - How often to poll in milliseconds (default: 5000)
 * @param options.useMockData - Use mock data instead of real API (default: true for now)
 *
 * @returns Graph data, loading state, error state, and manual refetch function
 */
export function useGraphData(options: UseGraphDataOptions = {}): UseGraphDataReturn {
  const { pollingInterval = 5000, useMockData = false } = options;

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);
  const isInitialLoadRef = useRef<boolean>(true);

  /**
   * Fetch and process graph data with diff-based updates
   */
  const fetchAndProcessData = useCallback(async () => {
    try {
      // Use mock or real API based on configuration
      const data = useMockData
        ? await fetchGraphDataMock()
        : await fetchGraphDataV1();

      // Always load data on initial fetch, then check changes flag for subsequent polls
      const shouldProcess = isInitialLoadRef.current || data.changes;

      if (shouldProcess) {
        // Parse JSON diagram with metrics
        const { nodes: newNodes, edges: newEdges } = parseGraphData(
          data.diagram,
          data.metrics
        );

        if (isInitialLoadRef.current) {
          // Initial load - use all new data
          console.log('Initial load, building graph...');
          console.log(`Loaded ${newNodes.length} nodes and ${newEdges.length} edges`);

          if (isMountedRef.current) {
            setNodes(newNodes);
            setEdges(newEdges);
            setError(null);
          }

          isInitialLoadRef.current = false;
        } else {
          // Subsequent update - use diff
          console.log('Changes detected, computing diff...');

          setNodes(currentNodes => {
            setEdges(currentEdges => {
              // Compute diff
              const diff = diffGraphData(currentNodes, currentEdges, newNodes, newEdges);

              console.log('Diff summary:', {
                nodesToAdd: diff.nodesToAdd.length,
                nodesToUpdate: diff.nodesToUpdate.length,
                nodesToRemove: diff.nodesToRemove.length,
                edgesToAdd: diff.edgesToAdd.length,
                edgesToRemove: diff.edgesToRemove.length,
              });

              if (diff.hasChanges) {
                // Apply diff
                const { nodes: updatedNodes, edges: updatedEdges } = applyGraphDiff(
                  currentNodes,
                  currentEdges,
                  diff
                );

                // Update nodes state from within setEdges
                if (isMountedRef.current) {
                  setNodes(updatedNodes);
                }

                // Return updated edges (this is what setEdges expects)
                return updatedEdges;
              } else {
                console.log('Diff found no actual changes');
                return currentEdges;
              }
            });

            // Return current nodes (unchanged since we update inside setEdges)
            return currentNodes;
          });

          if (isMountedRef.current) {
            setError(null);
          }
        }
      } else {
        console.log('No changes flag, keeping existing graph');
      }

      if (isMountedRef.current) {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching graph data:', err);
      if (isMountedRef.current) {
        setError(err instanceof Error ? err : new Error('Unknown error occurred'));
        setLoading(false);
      }
    }
  }, [useMockData]);

  /**
   * Manual refetch function
   */
  const refetch = useCallback(async () => {
    setLoading(true);
    await fetchAndProcessData();
  }, [fetchAndProcessData]);

  /**
   * Set up polling on mount
   */
  useEffect(() => {
    isMountedRef.current = true;

    // Initial fetch
    fetchAndProcessData();

    // Set up polling interval
    intervalRef.current = setInterval(() => {
      fetchAndProcessData();
    }, pollingInterval);

    // Cleanup on unmount
    return () => {
      isMountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchAndProcessData, pollingInterval]);

  return {
    nodes,
    edges,
    loading,
    error,
    refetch,
    setNodes,
    setEdges,
  };
}
