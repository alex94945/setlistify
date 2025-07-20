import axios from 'axios';

export const fetcher = (url: string) => axios.get(url).then((res) => res.data);

export interface Artist {
  name: string;
  mbid: string;
  disambiguation?: string;
}
