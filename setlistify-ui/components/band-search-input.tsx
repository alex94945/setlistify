'use client';

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { fetcher, Artist } from '@/lib/api';

interface BandSearchInputProps {
  onSelect: (artist: Artist) => void;
}

export default function BandSearchInput({ onSelect }: BandSearchInputProps) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [query]);

  const { data: artists, error } = useSWR<Artist[]>(
    debouncedQuery ? `/searchArtist?q=${debouncedQuery}` : null,
    fetcher
  );

  return (
    <div className="relative w-full max-w-md">
      <label htmlFor="band-search" className="sr-only">Search for a band</label>
      <input
        id="band-search"
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g., Radiohead"
        className="w-full px-4 py-2 text-gray-900 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-accent"
        autoComplete="off"
        aria-autocomplete="list"
        aria-controls="band-results"
      />
      {debouncedQuery && artists && (
        <ul id="band-results" role="listbox" className="absolute z-10 w-full mt-1 overflow-auto text-base bg-white border border-gray-300 rounded-md shadow-lg max-h-60 focus:outline-none sm:text-sm">
          {error && <li className="px-4 py-2 text-red-500">Error fetching artists.</li>}
          {!error && !artists && <li className="px-4 py-2 text-gray-500">Searching...</li>}
          {artists && artists.length === 0 && <li className="px-4 py-2 text-gray-500">No bands found.</li>}
          {artists.map((artist) => (
              <li
                key={artist.mbid}
                role="option"
                aria-selected="false"
                onClick={() => {
                  onSelect(artist);
                  setQuery(artist.name);
                  setDebouncedQuery('');
                }}
                className="relative px-4 py-2 cursor-pointer select-none hover:bg-purple-100"
              >
                {artist.name}
                {artist.disambiguation && <span className="ml-2 text-sm text-gray-500">({artist.disambiguation})</span>}
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
