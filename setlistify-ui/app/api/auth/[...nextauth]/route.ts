import NextAuth from 'next-auth';
import SpotifyProvider from 'next-auth/providers/spotify';

const handler = NextAuth({
  providers: [
    SpotifyProvider({
      clientId: process.env.SPOTIFY_CLIENT_ID ?? '',
      clientSecret: process.env.SPOTIFY_CLIENT_SECRET ?? '',
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  pages: {
    signIn: '/auth/signin',
    error: '/auth/signin', // Redirect errors to the custom sign-in page
  },
});

export { handler as GET, handler as POST };
