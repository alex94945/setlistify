'use client';

import React, { useEffect, useState } from 'react';

import axios from 'axios';

interface SetlistData {
  songs: string[];
  // showsMeta?: { date: string; venue: string; city: string }[];
}

interface PreviewSetlistProps {
  artistName: string;
  onSetlistReady: (songs: string[]) => void;
}

function ProgressLoader({ message, step, total }: { message: string; step: number; total: number }) {
  const progress = total > 0 ? (step / total) * 100 : 0;
  
  return (
    <div className="space-y-4">
      <div className="text-center">
        <p className="text-lg font-medium text-gray-900 mb-2">{message}</p>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500 mt-2">Step {step} of {total}</p>
      </div>
      <div className="space-y-4 animate-pulse">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-200 rounded-md"></div>
        ))}
      </div>
    </div>
  );
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
  
  const [setlist, setSetlist] = useState<SetlistData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [progressStep, setProgressStep] = useState<number>(0);
  const [totalSteps, setTotalSteps] = useState<number>(5);

  useEffect(() => {
    const fetchSetlist = () => {
      if (!artistName) return;
      
      setLoading(true);
      setError(null);
      setProgressMessage('Connecting to agent...');
      setProgressStep(0);
      
      // Create EventSource for Server-Sent Events
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/api/agent/setlist?artistName=${encodeURIComponent(artistName)}`,
        { withCredentials: true }
      );
      
      // Handle incoming messages
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'progress') {
            setProgressMessage(data.message);
            setProgressStep(data.step);
            setTotalSteps(data.total);
          } else if (data.type === 'complete') {
            const setlistData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
            setSetlist(setlistData);
            setLoading(false);
            eventSource.close();
          } else if (data.type === 'error') {
            setError(data.message || 'Failed to load setlist. Please try again.');
            setLoading(false);
            eventSource.close();
          }
        } catch (parseError) {
          console.error('Error parsing SSE data:', parseError);
        }
      };
      
      // Handle connection errors
      eventSource.onerror = (event) => {
        console.error('EventSource error:', event);
        if (eventSource.readyState === EventSource.CLOSED) {
          setError('Connection lost. Please try again.');
          setLoading(false);
        }
      };
      
      // Cleanup function
      return () => {
        eventSource.close();
      };
    };
    
    const cleanup = fetchSetlist();
    return cleanup;
  }, [artistName]);

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
        {loading ? (
          progressMessage ? (
            <ProgressLoader message={progressMessage} step={progressStep} total={totalSteps} />
          ) : (
            <SkeletonLoader />
          )
        ) : (
          setlist && (
            <ul className="space-y-2">
              {setlist.songs.map((song: string, i: number) => (
                <li key={i} className="p-2 bg-gray-50 rounded-md">
                  {song}
                </li>
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  );
}
