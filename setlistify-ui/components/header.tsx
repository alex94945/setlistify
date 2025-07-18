'use client';

import React from 'react';
import SpotifyLoginButton from './spotify-login-button';

export default function Header() {
  return (
    <header className="w-full max-w-5xl px-4 py-4 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-gray-900">Setlistify</span>
        </div>
        <div>
          <SpotifyLoginButton />
        </div>
      </div>
    </header>
  );
}
