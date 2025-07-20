'use client';

import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import axios from 'axios';


interface CreatePlaylistProps {
  artistName: string;
  songs: string[];
  onComplete: () => void;
}

export default function CreatePlaylist({ artistName, songs, onComplete }: CreatePlaylistProps) {
  const { data: session } = useSession();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ playlist_url: string; playlist_name: string; } | null>(null);

  const handleCreatePlaylist = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    if (!session?.accessToken) {
      setError('Not authenticated. Please sign in again.');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post('/api/external/createPlaylist', {
        artist_name: artistName,
        songs: songs,
      }, {
        headers: {
          Authorization: `Bearer ${session.accessToken}`,
        }
      });
      setResult(response.data);
      onComplete();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create playlist.');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="w-full max-w-2xl p-8 text-center bg-white border border-gray-200 rounded-lg shadow-sm">
        <h2 className="text-lg font-medium text-green-600">Playlist Created!</h2>
        <p className="mt-2 text-sm text-gray-500">
          Your playlist{' '}
          <a href={result.playlist_url} target="_blank" rel="noopener noreferrer" className="font-medium text-purple-accent hover:underline">
            {result.playlist_name}
          </a>{' '}
          has been added to your Spotify library.
        </p>
        <div className="mt-6">
          <button
            onClick={() => window.location.reload()} // Simple way to reset state
            className="px-4 py-2 text-sm font-medium text-white bg-purple-accent rounded-md hover:bg-purple-700"
          >
            Create Another
          </button>
        </div>
      </div>
    );
  }

  const playlistName = `${artistName} Setlist`;

  return (
    <div className="w-full max-w-2xl p-8 text-center bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium text-gray-900">Ready to Go?</h2>
      <p className="mt-1 text-sm text-gray-500">Confirm to create a playlist for {artistName} with {songs.length} songs.</p>
      <div className="mt-6">
        <button
          onClick={handleCreatePlaylist}
          disabled={loading}
          className="w-full px-4 py-2 text-sm font-medium text-white bg-purple-accent rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating...' : 'Create Playlist'}
        </button>
      </div>
      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}
    </div>
  );
}
