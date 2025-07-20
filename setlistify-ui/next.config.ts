import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "i.scdn.co",
      },
      {
        protocol: "https",
        hostname: "**.fbcdn.net",
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/external/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ]
  }
};

export default nextConfig;
