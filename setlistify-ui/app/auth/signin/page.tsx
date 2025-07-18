'use client';

import { useSearchParams } from 'next/navigation';
import Header from '@/components/header';
import PageWrapper from '@/components/page-wrapper';
import SpotifyLoginButton from '@/components/spotify-login-button';

const errorMessages: { [key: string]: string } = {
  OAuthSignin: 'There was an issue with the sign-in provider. Please try again.',
  OAuthCallback: 'There was an issue processing the sign-in. Please try again.',
  OAuthCreateAccount: 'Could not create an account. Please try again with a different method.',
  EmailCreateAccount: 'Could not create an account with this email. Please try again.',
  Callback: 'There was an issue during the callback process. Please try again.',
  OAuthAccountNotLinked: 'This account is not linked. Please sign in with the original provider.',
  default: 'An unexpected error occurred. Please try again.',
};

export default function SignInPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error');
  const errorMessage = error ? errorMessages[error] || errorMessages.default : null;

  return (
    <PageWrapper>
      <Header />
      <div className="flex flex-col items-center justify-center flex-grow text-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-sm w-full">
          <h1 className="text-2xl font-bold mb-4">Welcome to Setlistify</h1>
          <p className="text-gray-600 mb-6">Connect your Spotify account to get started.</p>
          {errorMessage && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Oops!</strong>
              <span className="block sm:inline ml-2">{errorMessage}</span>
            </div>
          )}
          <SpotifyLoginButton />
        </div>
      </div>
    </PageWrapper>
  );
}
