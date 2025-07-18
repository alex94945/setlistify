'use client';

import React, { useEffect } from 'react';
import useSWR from 'swr';
import { fetcher, Artist } from '@/lib/api';

interface SetlistData {
  songs: string[];
  showsMeta: {
    date: string;
    venue: string;
    city: string;
  }[];
}

interface PreviewSetlistProps {
  artist: Artist | null;
  onSetlistReady: (songs: string[]) => void;
}

function SkeletonLoader() {
  return (
    <div className="space-y-4 animate-pulse">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="h-12 bg-gray-200 rounded-md"></div>
      ))}
    </div>
  );
}

export default function PreviewSetlist({ artist, onSetlistReady }: PreviewSetlistProps) {
  const { data, error } = useSWR<SetlistData>(
    artist ? `/api/setlist?mbid=${artist.mbid}` : null,
    fetcher
  );

  useEffect(() => {
    if (data?.songs) {
      onSetlistReady(data.songs);
    }
  }, [data, onSetlistReady]);

  return (
    <div className="w-full max-w-2xl p-8 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium text-gray-900">Preview Setlist</h2>
      <p className="mt-1 text-sm text-gray-500">Here is a combined setlist from the latest shows for {artist?.name}.</p>
      <div className="mt-4 text-left">
        {error && <p className="text-red-500">Failed to load setlist. Please try again.</p>}
        {!data && !error && <SkeletonLoader />}
        {data && (
          <ul className="space-y-2">
            {data.songs.map((song, i) => (
              <li key={i} className="p-2 bg-gray-50 rounded-md">
                {song}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
