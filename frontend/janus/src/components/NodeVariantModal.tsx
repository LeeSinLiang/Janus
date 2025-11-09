'use client';

import { useEffect, useRef } from 'react';
import { Variant } from '@/types/api';
import { API_BASE_URL } from '@/services/api';

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

interface NodeVariantModalProps {
  isOpen: boolean;
  onClose: () => void;
  variant1: Variant;
  variant2: Variant;
  onSelectVariant?: (variantNumber: 1 | 2) => void;
}

export default function NodeVariantModal({
  isOpen,
  onClose,
  variant1,
  variant2,
  onSelectVariant,
}: NodeVariantModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

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
        <h2 className="mb-8 text-center text-2xl font-semibold text-zinc-900">
          A/B Test Different Styles 
        </h2>

        {/* Two variants side by side */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Variant 1 */}
          <button
            onClick={() => onSelectVariant?.(1)}
            className="group rounded-xl border-2 border-zinc-200 p-6 text-left transition-all hover:border-blue-400 hover:bg-blue-50/50"
          >
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-zinc-900 mb-2">
                Version {variant1.variant_id}
              </h3>
              {variant1.metadata.hook && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hook</p>
                  <p className="text-sm text-zinc-700">{variant1.metadata.hook}</p>
                </div>
              )}
            </div>

            {/* Media Asset Display */}
            {variant1.asset && (() => {
              const mediaType = getMediaType(variant1.asset);
              const fullAssetUrl = getFullAssetUrl(variant1.asset);
              return mediaType ? (
                <div className="mb-4">
                  <p className="text-xs font-medium text-zinc-500 uppercase mb-2">Media</p>
                  {mediaType === 'image' ? (
                    <img
                      src={fullAssetUrl}
                      alt={`Variant ${variant1.variant_id} media`}
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
                {variant1.content}
              </p>
            </div>
            {variant1.metadata.hashtags && variant1.metadata.hashtags.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hashtags</p>
                <div className="flex flex-wrap gap-2">
                  {variant1.metadata.hashtags.map((tag, idx) => (
                    <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {variant1.metadata.reasoning && (
              <div>
                <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Reasoning</p>
                <p className="text-xs text-zinc-600 italic">{variant1.metadata.reasoning}</p>
              </div>
            )}
          </button>

          {/* Variant 2 */}
          <button
            onClick={() => onSelectVariant?.(2)}
            className="group rounded-xl border-2 border-zinc-200 p-6 text-left transition-all hover:border-blue-400 hover:bg-blue-50/50"
          >
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-zinc-900 mb-2">
                Version {variant2.variant_id}
              </h3>
              {variant2.metadata.hook && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hook</p>
                  <p className="text-sm text-zinc-700">{variant2.metadata.hook}</p>
                </div>
              )}
            </div>

            {/* Media Asset Display */}
            {variant2.asset && (() => {
              const mediaType = getMediaType(variant2.asset);
              const fullAssetUrl = getFullAssetUrl(variant2.asset);
              return mediaType ? (
                <div className="mb-4">
                  <p className="text-xs font-medium text-zinc-500 uppercase mb-2">Media</p>
                  {mediaType === 'image' ? (
                    <img
                      src={fullAssetUrl}
                      alt={`Variant ${variant2.variant_id} media`}
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
                {variant2.content}
              </p>
            </div>
            {variant2.metadata.hashtags && variant2.metadata.hashtags.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Hashtags</p>
                <div className="flex flex-wrap gap-2">
                  {variant2.metadata.hashtags.map((tag, idx) => (
                    <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {variant2.metadata.reasoning && (
              <div>
                <p className="text-xs font-medium text-zinc-500 uppercase mb-1">Reasoning</p>
                <p className="text-xs text-zinc-600 italic">{variant2.metadata.reasoning}</p>
              </div>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
