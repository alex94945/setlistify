import type { NextApiRequest, NextApiResponse } from 'next';
import httpProxy from 'http-proxy';

const API_URL = process.env.NEXT_PUBLIC_API_URL; // e.g., http://127.0.0.1:8000

const proxy = httpProxy.createProxyServer();

export const config = {
  api: {
    bodyParser: false,
  },
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  return new Promise<void>((resolve, reject) => {
    proxy.web(req, res, { target: API_URL, changeOrigin: true }, (err: Error) => {
      if (err) {
        console.error('Proxy error:', err);
        return reject(err);
      }
      resolve();
    });
  });
}
