'use client';

import { useSession, signIn, signOut } from 'next-auth/react';
import Image from 'next/image';
import SpotifyIcon from './spotify-icon';

export default function SpotifyLoginButton() {
  const { data: session, status } = useSession();

  if (status === 'loading') {
    return <div className="w-24 h-9 bg-gray-200 rounded-md animate-pulse" />;
  }

  if (session) {
    return (
      <div className="flex items-center space-x-4">
        <Image
          src={session.user?.image ?? ''}
          alt={session.user?.name ?? 'User avatar'}
          width={32}
          height={32}
          className="rounded-full"
        />
        <button
          onClick={() => signOut()}
          className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
        >
          Sign out
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => signIn('spotify')}
      className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-[#1DB954] rounded-md hover:bg-green-700"
    >
      <SpotifyIcon />
      Connect with Spotify
    </button>
  );
}
