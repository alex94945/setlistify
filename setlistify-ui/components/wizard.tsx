'use client';

import React, { useState, useCallback } from 'react';
import ProgressStepper from './progress-stepper';
import ChooseBand from './steps/choose-band';
import PreviewSetlist from './steps/preview-setlist';
import CreatePlaylist from './steps/create-playlist';


export default function Wizard() {
  const [step, setStep] = useState(0);
  const [artistName, setArtistName] = useState('');
  const [songs, setSongs] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  

  const handleSetlistReady = useCallback((songList: string[]) => {
    setSongs(songList);
    // Automatically advance to the next step (Create Playlist)
    setStep(2);
  }, []);

  const handleComplete = useCallback(() => {
    setIsComplete(true);
  }, []);

  const handleReset = useCallback(() => {
    setStep(0);
    setArtistName('');
    setSongs([]);
    setIsComplete(false);
  }, []);

  const next = () => setStep((s) => Math.min(s + 1, 2)); // 3 steps total, so max index is 2
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const stepComponents = [
    <ChooseBand key="choose-band" artistName={artistName} onArtistNameChange={setArtistName} next={next} />,
    <PreviewSetlist key="preview-setlist" artistName={artistName} onSetlistReady={handleSetlistReady} />,
    <CreatePlaylist key="create-playlist" artistName={artistName} songs={songs} onComplete={handleComplete} onReset={handleReset} />,
  ];

  return (
    <div className="flex flex-col items-center space-y-8 h-full">
      <ProgressStepper currentStep={step} />
      <div className="w-full flex-grow overflow-y-auto">
        {stepComponents[step]}
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
            (step === 0 && artistName.trim() === '') ||
            (step === 1 && songs.length === 0) ||
            step === stepComponents.length - 1 ||
            isComplete
          }
          className="px-4 py-2 text-sm font-medium text-white bg-purple-700 rounded-md hover:bg-purple-800 disabled:opacity-50"
        >
          {step === stepComponents.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  );
}
