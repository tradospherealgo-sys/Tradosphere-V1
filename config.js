/**
 * Tradosphere Configuration
 * Centralized API configuration for all frontend components
 *
 * Sets the backend API URL dynamically:
 * 1. Checks for NEXT_PUBLIC_API_URL environment variable (set by Vercel)
 * 2. Falls back to Railway production URL
 * 3. Falls back to localhost for development
 */

// Determine API base URL based on environment
const API_BASE_URL = (() => {
  // Check if running on Vercel with environment variable
  if (typeof window !== 'undefined') {
    // For Vercel: use NEXT_PUBLIC_API_URL if set
    if (window.__ENV__ && window.__ENV__.NEXT_PUBLIC_API_URL) {
      return window.__ENV__.NEXT_PUBLIC_API_URL;
    }
  }

  // Check if environment variable is injected into global scope
  if (typeof TRADOSPHERE_API_URL !== 'undefined') {
    return TRADOSPHERE_API_URL;
  }

  // Default to Railway production backend
  const backendUrl = 'https://tradosphere-v1-production.up.railway.app';

  // Allow localhost for development
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }

  return backendUrl;
})();

/**
 * Log the configured API URL (for debugging)
 */
if (typeof window !== 'undefined') {
  console.log('🌐 Tradosphere API URL configured:', API_BASE_URL);
}

/**
 * Export for use in modules
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_BASE_URL };
}
