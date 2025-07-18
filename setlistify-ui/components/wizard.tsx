'use client';

import React, { useState } from 'react';
import ProgressStepper from './progress-stepper';
import ChooseBand from './steps/choose-band';
import PreviewSetlist from './steps/preview-setlist';
import CreatePlaylist from './steps/create-playlist';
import { Artist } from '@/lib/api';

export default function Wizard() {
  const [step, setStep] = useState(0);
  const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
  const [songs, setSongs] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  const handleBandSelect = (artist: Artist) => {
    setSelectedArtist(artist);
  };

  const handleSetlistReady = (songList: string[]) => {
    setSongs(songList);
  };

  const handleComplete = () => {
    setIsComplete(true);
  };

  const steps = [
    <ChooseBand key="choose-band" onBandSelect={handleBandSelect} />,
    <PreviewSetlist key="preview-setlist" artist={selectedArtist} onSetlistReady={handleSetlistReady} />,
    <CreatePlaylist key="create-playlist" artist={selectedArtist} songs={songs} onComplete={handleComplete} />,
  ];

  const next = () => setStep((s) => Math.min(s + 1, steps.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  return (
    <div className="flex flex-col items-center space-y-8">
      <ProgressStepper currentStep={step} />
      <div className="w-full">
        {steps[step]}
      </div>
      <div className="flex justify-between w-full max-w-2xl">
        <button
          onClick={prev}
          disabled={step === 0 || isComplete}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Back
        </button>
        <button
          onClick={next}
          disabled={
            (step === 0 && !selectedArtist) ||
            (step === 1 && songs.length === 0) ||
            step === steps.length - 1 ||
            isComplete
          }
          className="px-4 py-2 text-sm font-medium text-white bg-purple-accent rounded-md hover:bg-purple-700 disabled:opacity-50"
        >
          {step === steps.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  );
}
