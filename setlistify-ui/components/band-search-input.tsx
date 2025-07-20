'use client';

import React from 'react';

interface BandSearchInputProps {
  onArtistNameChange: (name: string) => void;
  artistName: string;
}

const BandSearchInput: React.FC<BandSearchInputProps> = ({ onArtistNameChange, artistName }) => {
  return (
    <input
      type="text"
      value={artistName}
      onChange={(e) => onArtistNameChange(e.target.value)}
      placeholder="Enter artist name"
      className="w-full p-2 border rounded-md"
    />
  );
};

export default BandSearchInput;
