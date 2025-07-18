'use client';

import React from 'react';
import BandSearchInput from '../band-search-input';
import { Artist } from '@/lib/api';

interface ChooseBandProps {
  onBandSelect: (artist: Artist) => void;
}

export default function ChooseBand({ onBandSelect }: ChooseBandProps) {
  return (
    <div className="w-full max-w-2xl p-8 text-center bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium text-gray-900">Choose a Band</h2>
      <p className="mt-1 text-sm text-gray-500">Start by searching for your favorite band.</p>
      <div className="mt-4 flex justify-center">
        <BandSearchInput onSelect={onBandSelect} />
      </div>
    </div>
  );
}
