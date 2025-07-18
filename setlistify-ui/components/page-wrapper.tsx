import React from 'react';

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center w-full min-h-screen bg-gray-50">
      {children}
    </div>
  );
}
