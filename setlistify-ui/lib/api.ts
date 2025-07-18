import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const fetcher = (url: string) => api.get(url).then((res) => res.data);

export interface Artist {
  name: string;
  mbid: string;
  disambiguation?: string;
}
