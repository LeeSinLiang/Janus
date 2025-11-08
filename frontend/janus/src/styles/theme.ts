/**
 * Theme color constants for Janus application
 *
 * Use these constants throughout the app for consistent theming
 */

export const THEME_COLORS = {
  // UI Colors
  searchTab: '#F2F2F2',
  logo: '#FBAE2C',
  shareButton: '#FFF',
  whiteButton: '#FFF',

  // Node Colors
  nodeBackground: '#FFFFFF',
  nodeHighlightBorder: 'radial-gradient(247.65% 141.42% at 0% 100%, #4A02FF 0%, #831DEF 50%, #AA31E4 100%)',
  nodePendingBackground: '#65F57466', // Green with alpha

  // Button Colors
  approveButton: {
    background: '#A2FFAB',
    border: '#65F574',
  },
  rejectButton: {
    background: '#FF7F7F',
    border: '#FF3B3B',
  },
} as const;

/**
 * Gradient utilities for easy application
 */
export const GRADIENTS = {
  nodeHighlight: 'radial-gradient(247.65% 141.42% at 0% 100%, #4A02FF 0%, #831DEF 50%, #AA31E4 100%)',
} as const;

/**
 * Apply node highlight border style
 */
export function getNodeHighlightStyle() {
  return {
    border: '4px solid transparent',
    borderImage: `${GRADIENTS.nodeHighlight} 1`,
  };
}

/**
 * Get button styles by type
 */
export function getButtonStyle(type: 'approve' | 'reject') {
  const colors = type === 'approve' ? THEME_COLORS.approveButton : THEME_COLORS.rejectButton;
  return {
    background: colors.background,
    border: `1px solid ${colors.border}`,
  };
}
