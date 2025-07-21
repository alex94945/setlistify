'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import SpotifyIcon from './spotify-icon';

interface UserInfo {
  name: string;
  image?: string;
  id: string;
}

interface AuthStatus {
  authenticated: boolean;
  user?: UserInfo;
}

export default function SpotifyLoginButton() {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/status`,
        { 
          withCredentials: true,
          timeout: 3000 // 3 second timeout
        }
      );
      setAuthStatus(response.data);
    } catch (error: any) {
      console.log('Auth status check failed (backend may be down):', error?.message || 'Unknown error');
      setAuthStatus({ authenticated: false });
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    // Redirect to our backend's Spotify auth endpoint
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth`;
  };

  const handleLogout = async () => {
    try {
      await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/logout`,
        { withCredentials: true }
      );
      // Refresh the page or update state
      window.location.reload();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="w-48 h-12 bg-gray-200 rounded-md animate-pulse" />
    );
  }

  if (authStatus?.authenticated && authStatus.user) {
    return (
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          {authStatus.user.image && (
            <img 
              src={authStatus.user.image} 
              alt="Profile" 
              className="w-8 h-8 rounded-full" 
            />
          )}
          <span className="text-sm font-medium text-gray-700">
            {authStatus.user.name}
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Sign out
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={handleLogin}
      className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-[#1DB954] rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
    >
      <SpotifyIcon />
      Connect with Spotify
    </button>
  );
}
