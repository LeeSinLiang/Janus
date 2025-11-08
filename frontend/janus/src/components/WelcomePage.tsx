'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { generateStrategy } from '@/services/api';

export default function WelcomePage() {
  const router = useRouter();
  const [productDescription, setProductDescription] = useState('');
  const [gtmGoals, setGtmGoals] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!productDescription.trim() || !gtmGoals.trim()) {
      return;
    }

    setIsLoading(true);

    try {
      await generateStrategy({
        product_description: productDescription,
        gtm_goals: gtmGoals,
        campaign_name: 'Campaign',
      });

      // Navigate to canvas after successful generation
      router.push('/canvas');
    } catch (error) {
      console.error('Failed to generate strategy:', error);
      setIsLoading(false);
      // TODO: Show error message to user
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  if (isLoading) {
    return (
      <div 
        className="relative h-screen w-screen bg-gray-50"
        style={{
          backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
          backgroundSize: '16px 16px'
        }}
      >
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="mb-8 animate-spin rounded-full h-16 w-16 border-b-4 border-orange-500"></div>
          <p className="text-xl text-gray-600 font-medium">Generating your campaign...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="relative h-screen w-screen bg-gray-50 overflow-hidden"
      style={{
        backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
        backgroundSize: '16px 16px'
      }}
    >
      <div className="absolute inset-0 flex flex-col items-center justify-center px-4">
        {/* Janus Logo */}
        <div className="mb-12">
          <h1 className="text-6xl font-bold text-orange-500">Janus</h1>
        </div>

        {/* Welcome Message */}
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-indigo-950 mb-2">Hey Buzz!</h2>
          <h3 className="text-5xl font-bold text-indigo-950 mb-4">
            Building is your passion,
          </h3>
          <h3 className="text-5xl font-bold text-indigo-950 mb-6">
            marketing is mine.
          </h3>
          <p className="text-xl text-gray-600">Ready to plan your next campaign?</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="w-full max-w-4xl space-y-4">
          {/* Product Description Input */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm px-6 py-4">
            <label className="block text-gray-600 text-base mb-2">
              Product Description :
            </label>
            <input
              type="text"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe your product briefly (e.g. AI photo editor)"
              className="w-full text-gray-400 text-base outline-none bg-transparent"
            />
          </div>

          {/* GTM Goals Input with Submit Button */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm px-6 py-4 flex items-center gap-4">
            <div className="flex-1">
              <label className="block text-gray-600 text-base mb-2">
                GTM Goals :
              </label>
              <input
                type="text"
                value={gtmGoals}
                onChange={(e) => setGtmGoals(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="What's your marketing goal?"
                className="w-full text-gray-400 text-base outline-none bg-transparent"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="flex-shrink-0 w-12 h-12 rounded-full bg-orange-500 hover:bg-orange-600 transition-colors flex items-center justify-center"
              disabled={!productDescription.trim() || !gtmGoals.trim()}
            >
              <svg
                className="w-6 h-6 text-white transform rotate-45"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
