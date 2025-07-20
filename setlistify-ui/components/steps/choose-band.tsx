'use client';

import React, { useState } from 'react';
import BandSearchInput from '../band-search-input';
interface ChooseBandProps {
  onArtistNameChange: (name: string) => void;
  artistName: string;
  next: () => void;
}

export default function ChooseBand({ onArtistNameChange, artistName, next }: ChooseBandProps) {
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (artistName.trim() !== '') {
      next();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full flex justify-center">
      <div className="w-full max-w-2xl p-8 text-center bg-white border border-gray-200 rounded-lg shadow-sm">
        <h2 className="text-lg font-medium text-gray-900">Choose a Band</h2>
        <p className="mt-1 text-sm text-gray-500">Start by searching for your favorite band, then press Next.</p>
        <div className="mt-4 flex justify-center">
          <BandSearchInput 
            artistName={artistName}
            onArtistNameChange={onArtistNameChange}
          />
        </div>
      </div>
    </form>
  );
}
