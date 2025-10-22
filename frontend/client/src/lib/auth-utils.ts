import { useAuth } from '../contexts/AuthContext';

// Utility function to handle API responses and check for auth errors
export const handleApiResponse = async (response: Response, redirectToHome?: () => void) => {
  if (response.status === 401) {
    console.log('🔐 Authentication failed - redirecting to home');
    
    // Sign out the user
    const { signOut } = useAuth();
    await signOut();
    
    // Redirect to home page
    if (redirectToHome) {
      redirectToHome();
    } else if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
    
    throw new Error('Authentication failed');
  }
  
  return response;
};

// Wrapper for fetch that automatically handles auth errors
export const authFetch = async (url: string, options: RequestInit = {}, redirectToHome?: () => void) => {
  try {
    const response = await fetch(url, options);
    await handleApiResponse(response, redirectToHome);
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Hook for making authenticated API calls with automatic redirect
export const useAuthenticatedFetch = () => {
  const { signOut } = useAuth();
  
  const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 401) {
        console.log('🔐 Authentication failed - signing out and redirecting');
        await signOut();
        window.location.href = '/';
        throw new Error('Authentication failed');
      }
      
      return response;
    } catch (error) {
      console.error('Authenticated API request failed:', error);
      throw error;
    }
  };
  
  return authenticatedFetch;
};