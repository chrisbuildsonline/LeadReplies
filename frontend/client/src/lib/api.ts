/**
 * Get the API base URL based on environment
 */
export function getApiUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  
  // If VITE_API_URL is explicitly set, use it
  if (envUrl) {
    return envUrl;
  }
  
  // In production, use same origin (proxy approach)
  if (import.meta.env.PROD) {
    return window.location.origin;
  }
  
  // Development fallback
  return 'http://localhost:6070';
}

export const API_URL = getApiUrl();