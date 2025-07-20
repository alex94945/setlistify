'use client';

import React, { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';

interface SetlistData {
  songs: string[];
  // showsMeta?: { date: string; venue: string; city: string }[];
}

interface PreviewSetlistProps {
  artistName: string;
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

export default function PreviewSetlist({ artistName, onSetlistReady }: PreviewSetlistProps) {
  const { data: session } = useSession();
  const [setlist, setSetlist] = useState<SetlistData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSetlist = async () => {
      if (!artistName || !session?.accessToken) return;
      setLoading(true);
      setError(null);
      try {
        const response = await axios.post(
          '/api/external/agent/setlist',
          { artistName },
          {
            headers: {
              Authorization: `Bearer ${session.accessToken}`,
            },
          }
        );
        const data = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
        setSetlist(data);
      } catch (err) {
        setError('Failed to load setlist. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchSetlist();
  }, [artistName, session?.accessToken]);

  useEffect(() => {
    if (setlist?.songs && setlist.songs.length > 0) {
      onSetlistReady(setlist.songs);
    }
  }, [setlist, onSetlistReady]);

  return (
    <div className="w-full max-w-2xl p-8 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium text-gray-900">Preview Setlist</h2>
      <h3 className="text-xl font-semibold">{artistName}</h3>
      <p className="mt-1 text-sm text-gray-500">Here is a combined setlist from the latest shows for {artistName}.</p>
      <div className="mt-4 text-left">
        {error && <p className="text-red-500">{error}</p>}
        {loading && <SkeletonLoader />}
        {setlist && (
          <ul className="space-y-2">
            {setlist.songs.map((song: string, i: number) => (
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
