'use client';

import { useSession } from 'next-auth/react';
import Header from '@/components/header';
import PageWrapper from '@/components/page-wrapper';
import SpotifyLoginButton from '@/components/spotify-login-button';
import Wizard from '@/components/wizard';

export default function Home() {
  const { data: session, status } = useSession();
  return (
    <PageWrapper>
      <Header />
      <div className="flex flex-col items-center justify-center flex-grow">
        {status === 'loading' ? (
          <div className="text-center">
            <p className="text-gray-500">Loading...</p>
          </div>
        ) : session ? (
          <Wizard />
        ) : (
          <div className="text-center max-w-2xl mx-auto">
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              From Setlist to Playlist, Instantly
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Relive your favorite concert memories or get hyped for an upcoming show. With Setlistify, you can find an artist's latest setlist and instantly turn it into a Spotify playlist. It's the perfect way to learn the songs before you go or keep the experience alive long after the encore.
            </p>
            <div className="mt-10">
              <SpotifyLoginButton />
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
