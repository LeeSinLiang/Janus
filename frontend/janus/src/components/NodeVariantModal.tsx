'use client';

import { useEffect, useRef } from 'react';
import { Variant } from '@/types/api';
import { API_BASE_URL } from '@/services/api';
import VariantMetricsBox from './VariantMetricsBox';

// Helper function to determine media type based on file extension
function getMediaType(assetUrl: string): 'image' | 'video' | null {
  if (!assetUrl) return null;

  const extension = assetUrl.split('.').pop()?.toLowerCase();

  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
  const videoExtensions = ['mp4', 'webm', 'ogg', 'mov'];

  if (imageExtensions.includes(extension || '')) return 'image';
  if (videoExtensions.includes(extension || '')) return 'video';

  return null;
}

// Helper function to get full asset URL
function getFullAssetUrl(assetPath: string): string {
  if (!assetPath) return '';

  // If the path already starts with http:// or https://, return as-is
  if (assetPath.startsWith('http://') || assetPath.startsWith('https://')) {
    return assetPath;
  }

  // Otherwise, prepend the backend URL
  // Remove trailing slash from API_BASE_URL and leading slash from assetPath if present
  const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const path = assetPath.startsWith('/') ? assetPath : `/${assetPath}`;

  return `${baseUrl}${path}`;
}

interface VariantMetrics {
  likes: number;
  retweets: number;
  comments: number;
  positivity: number;
}

interface NodeVariantModalProps {
  isOpen: boolean;
  onClose: () => void;
  variant1?: Variant; // Keep for backward compatibility
  variant2?: Variant; // Keep for backward compatibility
  variants?: Variant[]; // New prop for multiple variants
  onSelectVariant?: (variantNumber: 1 | 2) => void;
  variantMetrics?: {
    A: VariantMetrics;
    B: VariantMetrics;
  };
}

export default function NodeVariantModal({
  isOpen,
  onClose,
  variant1,
  variant2,
  variants,
  onSelectVariant,
  variantMetrics,
}: NodeVariantModalProps) {
  // Default metrics if not provided
  const defaultMetrics: VariantMetrics = {
    likes: 0,
    retweets: 0,
    comments: 0,
    positivity: 0,
  };

  const metricsA = variantMetrics?.A ?? defaultMetrics;
  const metricsB = variantMetrics?.B ?? defaultMetrics;
  const modalRef = useRef<HTMLDivElement>(null);

  // Process variants - support both old props and new variants array
  const allVariants = variants || (variant1 && variant2 ? [variant1, variant2] : []);

  // Group variants by regeneration status
  // Sort by created_at (newest first) and group by variant_id
  const variantsByGeneration: { label: string; variantsA: Variant[]; variantsB: Variant[] }[] = [];

  if (allVariants.length > 0) {
    // Sort all variants by created_at
    const sortedVariants = [...allVariants].sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();
      return dateB - dateA; // Newest first
    });

    // Group into generations (every 2 variants = 1 generation)
    const variantsA = sortedVariants.filter(v => v.variant_id === 'A');
    const variantsB = sortedVariants.filter(v => v.variant_id === 'B');

    // Create generations (pairs of A and B)
    const maxGenerations = Math.max(variantsA.length, variantsB.length);
    for (let i = 0; i < maxGenerations; i++) {
      const isRegenerated = variantsA[i]?.metadata?.regenerated || variantsB[i]?.metadata?.regenerated;

      // Label logic:
      // - Index 0 (newest): Show "🔄 Regenerated (Latest)" if regenerated, else "✨ Current"
      // - Index > 0 (older): Show "🔄 Regenerated" if regenerated, else "📝 Original"
      let label: string;
      if (i === 0) {
        label = isRegenerated ? '🔄 Regenerated (Latest)' : '✨ Current';
      } else {
        label = isRegenerated ? `🔄 Regenerated (v${maxGenerations - i})` : `📝 Original (v${maxGenerations - i})`;
      }

      variantsByGeneration.push({
        label,
        variantsA: variantsA[i] ? [variantsA[i]] : [],
        variantsB: variantsB[i] ? [variantsB[i]] : [],
      });
    }
  }

  // If no variants processed, fall back to old props
  const hasMultipleGenerations = variantsByGeneration.length > 1;
  const currentGeneration = variantsByGeneration[0] || { label: 'Current', variantsA: variant1 ? [variant1] : [], variantsB: variant2 ? [variant2] : [] };
  const currentVariantA = currentGeneration.variantsA[0];
  const currentVariantB = currentGeneration.variantsB[0];

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Close modal when clicking outside
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;
  if (!currentVariantA && !currentVariantB) return null;

  // Helper to render a single variant
  const renderVariant = (variant: Variant | undefined, variantNumber: 1 | 2, metrics: VariantMetrics) => {
    if (!variant) return null;

    return (
      <div>
        <button
          onClick={() => onSelectVariant?.(variantNumber)}
          className="w-full group rounded-xl border-2 border-zinc-200 p-6 text-left transition-all hover:border-blue-400 hover:bg-blue-50/50"
        >
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-zinc-900 mb-2">
              Version {variant.variant_id}
            </h3>
            {variant.metadata.hook && (
              <div className="mb-3">
                <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hook</p>
                <p className="text-sm text-zinc-700">{variant.metadata.hook}</p>
              </div>
            )}
          </div>

          {/* Media Asset Display */}
          {variant.asset && (() => {
            const mediaType = getMediaType(variant.asset);
            const fullAssetUrl = getFullAssetUrl(variant.asset);
            return mediaType ? (
              <div className="mb-4">
                <p className="text-xs font-medium text-zinc-500 uppercase mb-2">Media</p>
                {mediaType === 'image' ? (
                  <img
                    src={fullAssetUrl}
                    alt={`Variant ${variant.variant_id} media`}
                    className="w-full rounded-lg border border-zinc-200 object-cover"
                    style={{ maxHeight: '300px' }}
                  />
                ) : (
                  <video
                    src={fullAssetUrl}
                    controls
                    className="w-full rounded-lg border border-zinc-200"
                    style={{ maxHeight: '300px' }}
                  >
                    Your browser does not support the video tag.
                  </video>
                )}
              </div>
            ) : null;
          })()}

          <div className="mb-3">
            <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Content</p>
            <p className="text-sm leading-relaxed text-zinc-700 whitespace-pre-wrap">
              {variant.content}
            </p>
          </div>
          {variant.metadata.hashtags && variant.metadata.hashtags.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hashtags</p>
              <div className="flex flex-wrap gap-2">
                {variant.metadata.hashtags.map((tag: string, idx: number) => (
                  <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}
          {variant.metadata.reasoning && (
            <div>
              <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Reasoning</p>
              <p className="text-xs text-zinc-600 italic">{variant.metadata.reasoning}</p>
            </div>
          )}
        </button>

        {/* Metrics */}
        <VariantMetricsBox metrics={metrics} />
      </div>
    );
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-4xl rounded-2xl bg-white p-8 shadow-2xl"
        style={{ maxHeight: '90vh', overflow: 'auto' }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-6 top-6 text-zinc-400 transition-colors hover:text-zinc-600"
          aria-label="Close modal"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {/* Modal title */}
        <h2 className="mb-2 text-center text-2xl font-semibold text-zinc-900">
          A/B Test Different Styles
        </h2>
        <p className="mb-6 text-center text-sm text-zinc-500">
          {currentGeneration.label}
        </p>

        {/* Current generation - Two variants side by side */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 mb-6">
          {renderVariant(currentVariantA, 1, metricsA)}
          {renderVariant(currentVariantB, 2, metricsB)}
        </div>

        {/* Previous versions (if any) */}
        {hasMultipleGenerations && (
          <details className="mt-8 border-t pt-4" open>
            <summary className="cursor-pointer text-sm font-medium text-zinc-600 hover:text-zinc-900">
              📜 View Previous Versions ({variantsByGeneration.length - 1})
            </summary>
            <div className="mt-4 space-y-6">
              {variantsByGeneration.slice(1).map((generation, idx) => (
                <div key={idx} className="border-t pt-4">
                  <h3 className="mb-3 text-sm font-semibold text-zinc-700">{generation.label}</h3>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    {generation.variantsA[0] && (
                      <div>
                        <div className="rounded-lg border border-zinc-200 p-4 mb-3">
                          <p className="mb-2 text-xs font-medium text-zinc-500 uppercase">Variant A</p>

                          {/* Media Asset Display for Variant A */}
                          {generation.variantsA[0].asset && (() => {
                            const mediaType = getMediaType(generation.variantsA[0].asset);
                            const fullAssetUrl = getFullAssetUrl(generation.variantsA[0].asset);
                            return mediaType ? (
                              <div className="mb-3">
                                {mediaType === 'image' ? (
                                  <img
                                    src={fullAssetUrl}
                                    alt="Variant A media"
                                    className="w-full rounded-lg border border-zinc-200 object-cover mb-2"
                                    style={{ maxHeight: '200px' }}
                                  />
                                ) : (
                                  <video
                                    src={fullAssetUrl}
                                    controls
                                    className="w-full rounded-lg border border-zinc-200 mb-2"
                                    style={{ maxHeight: '200px' }}
                                  >
                                    Your browser does not support the video tag.
                                  </video>
                                )}
                              </div>
                            ) : null;
                          })()}

                          <p className="text-sm text-zinc-700 whitespace-pre-wrap">{generation.variantsA[0].content}</p>
                        </div>

                        {/* Metrics for Variant A */}
                        <VariantMetricsBox metrics={metricsA} />
                      </div>
                    )}
                    {generation.variantsB[0] && (
                      <div>
                        <div className="rounded-lg border border-zinc-200 p-4 mb-3">
                          <p className="mb-2 text-xs font-medium text-zinc-500 uppercase">Variant B</p>

                          {/* Media Asset Display for Variant B */}
                          {generation.variantsB[0].asset && (() => {
                            const mediaType = getMediaType(generation.variantsB[0].asset);
                            const fullAssetUrl = getFullAssetUrl(generation.variantsB[0].asset);
                            return mediaType ? (
                              <div className="mb-3">
                                {mediaType === 'image' ? (
                                  <img
                                    src={fullAssetUrl}
                                    alt="Variant B media"
                                    className="w-full rounded-lg border border-zinc-200 object-cover mb-2"
                                    style={{ maxHeight: '200px' }}
                                  />
                                ) : (
                                  <video
                                    src={fullAssetUrl}
                                    controls
                                    className="w-full rounded-lg border border-zinc-200 mb-2"
                                    style={{ maxHeight: '200px' }}
                                  >
                                    Your browser does not support the video tag.
                                  </video>
                                )}
                              </div>
                            ) : null;
                          })()}

                          <p className="text-sm text-zinc-700 whitespace-pre-wrap">{generation.variantsB[0].content}</p>
                        </div>

                        {/* Metrics for Variant B */}
                        <VariantMetricsBox metrics={metricsB} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
