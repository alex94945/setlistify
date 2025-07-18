### **Setlistify — Public Web UI Specification (v0.9)**

> **Goal**: A one-page, mobile-friendly web app that lets any visitor connect their Spotify account, choose a band, preview the latest tour set-list, and create a playlist in their own Spotify library.

---

## 1. Tech stack

| Layer           | Choice                                                                    | Rationale                                                                                     |
| --------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Front-end**   | **Next.js 14 (App Router)**, TypeScript, Tailwind CSS                     | Zero-config deployment on Vercel/Fly, SSR for SEO, easy form handling.                        |
| **Auth widget** | NextAuth.js (Spotify provider)                                            | Handles the OAuth redirect, cookie session, CSRF.                                             |
| **Server APIs** | Next.js API routes (same repo) or existing FastAPI service behind `/api/` | Keep UI + agent server colocated for simplest deploy; can proxy if you keep FastAPI separate. |
| **State**       | React context (`SessionProvider`) + SWR for fetches                       | Removes custom Redux/MobX boiler-plate.                                                       |
| **Hosting**     | Vercel (frontend) + Fly.io / Render (FastAPI)                             | Both offer free tiers; easy env-var management.                                               |

---

## 2. Page anatomy (single route `/`)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Header                                                                 │
│ ────────────────────────────────────────────────────────────────────── │
│  • Logo  ·  “Setlistify”                                              │
│  • Right-side: [Connect Spotify]  (or user avatar + logout)           │
│                                                                       │
│ Main panel (holds the 3 wizard steps)                                 │
│ ────────────────────────────────────────────────────────────────────── │
│  1 Choose Band   2 Preview Setlist   3 Create Playlist                │
│                                                                       │
│  STEP 1 (default)                                                     │
│  ┌───────────────┐                                                    │
│  │  [🔍]  input  │  «Debounced autocomplete from setlist.fm»          │
│  └───────────────┘                                                    │
│  [Next ▶] (disabled until band chosen)                                │
│                                                                       │
│  STEP 2                                                               │
│  • Accordion with show date, city, tour name (p=1..N)                 │
│  • Inside each: ordered list of songs                                 │
│  [◀ Back]   [Looks good →]                                            │
│                                                                       │
│  STEP 3                                                               │
│  🎉 “Playlist created!”                                               │
│  [Open in Spotify]  [Start another]                                   │
│                                                                       │
│ Snackbar / toast area (error, success)                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. User flow & states

| State                  | Trigger → Next state                      | UI specifics                                                                                         |
| ---------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **A. Anonymous**       | App loads, no `session` cookie            | Header shows “Connect Spotify”. Steps are disabled; attempting to search band prompts auth banner.   |
| **B. Authorizing**     | Click “Connect Spotify”                   | NextAuth opens `/api/auth/signin?provider=spotify`. Spotify consent → redirect back with JWT cookie. |
| **C. Authenticated**   | Session cookie valid                      | Header shows avatar + displayName; wizard enabled.                                                   |
| **D. Band chosen**     | User selects item from autocomplete       | “Next” button active; store `{artistName, mbid}` in React context.                                   |
| **E. Setlist preview** | Fetch `/api/setlist?mbid=…&shows=N`       | Show first 50 songs (deduped). Allow toggling N (1–5).                                               |
| **F. Created**         | POST `/api/playlist` returns playlist URL | Confetti animation; deep link to Spotify.                                                            |

---

## 4. Components (React)

| Component                  | Props                 | Responsibilities                                                                           |
| -------------------------- | --------------------- | ------------------------------------------------------------------------------------------ |
| `<SpotifyLoginButton />`   | `session`             | Calls `signIn('spotify')`; disables when loading.                                          |
| `<BandSearchInput />`      | `onSelect(artistObj)` | Debounced fetch to `/api/searchArtist?q=` returns array of `{name, mbid, disambiguation}`. |
| `<SetlistPreview />`       | `mbid`, `shows`       | Fetch + display accordion; emits `onReady(songs[])`.                                       |
| `<CreatePlaylistButton />` | `songs[]`             | POST `/api/playlist`; handles loading + error toasts.                                      |
| `<ProgressStepper />`      | `currentStep`         | Visual 1-2-3 tracker.                                                                      |
| `<Toast />`                | global                | Uses Headless UI/Aria-live for a11y.                                                       |

---

## 5. Back-end API contract

| Route               | Method | Body / Query                  | Returns                                      |
| ------------------- | ------ | ----------------------------- | -------------------------------------------- |
| `/api/searchArtist` | GET    | `q`                           | `[ { name, mbid } ]`                         |
| `/api/setlist`      | GET    | `mbid`, `shows` (default = 3) | `{ songs: [str], showsMeta: [date, venue] }` |
| `/api/playlist`     | POST   | `{ artist, songs[] }`         | `{ url }` or 4xx/5xx                         |

All routes require `req.session.user.accessToken` from NextAuth; handler binds token with `build_agent_for_token(token)`.

---

## 6. Styling & UX

* **Tailwind tokens**

  * font: `font-sans` (Inter), purple accent `#7C3AED`.
  * stepper circles: `w-8 h-8 rounded-full border-2 border-gray-300`.
* **Mobile** – vertical wizard; Search/Next stacked; use `sticky` footer for CTA.
* **Skeleton loaders** for setlist fetch (3 gray bars).
* **Error handling**

  * 401 → prompt re-login (token revoked).
  * 429 or setlist.fm quota → “Too many requests; try again in a minute.”

---

## 7. Deployment & env vars

| Name                         | Frontend (Vercel)                                  | Backend (Fly / Render)                |
| ---------------------------- | -------------------------------------------------- | ------------------------------------- |
| `NEXTAUTH_URL`               | `https://setlistify.app`                           | n/a                                   |
| `NEXTAUTH_SECRET`            | ✅                                                  | n/a                                   |
| `SPOTIFY_CLIENT_ID / SECRET` | ✅                                                  | ✅                                     |
| `SPOTIFY_REDIRECT_URI`       | `https://setlistify.app/api/auth/callback/spotify` | `https://api.setlistify.app/callback` |
| `SESSION_SECRET`             | n/a                                                | ✅                                     |
| `SETLIST_API_KEY`            | n/a                                                | ✅                                     |
| `TOGETHER_API_KEY`           | n/a                                                | ✅                                     |

*Frontend’s `/api/*` routes proxy to backend origin using
`NEXT_PUBLIC_API_BASE=https://api.setlistify.app`.*

---

## 8. Accessibility & SEO

* Use `label` + `aria-describedby` on inputs.
* Page title updates per step: “Setlistify – Choose Band”, “ – Preview”, “ – Done”.
* OG tags: playlist art URL (Spotify’s `/images/playlist.png`) when created.

---

## 9. Stretch enhancements

| Idea                                     | Effort | Notes                                                           |
| ---------------------------------------- | ------ | --------------------------------------------------------------- |
| “Latest N shows” slider                  | S      | let power users merge 1–5 shows.                                |
| Dark mode toggle                         | S      | Tailwind `dark:` classes.                                       |
| Persist past playlists                   | M      | Store `{sid, playlistId, artist}` in Redis; surface in sidebar. |
| Share link generator                     | M      | Shorten `spotify.com/playlist/...` via `tinyurl.com`.           |
| Band autocomplete powered by MusicBrainz | M      | Richer search & avatars.                                        |

---

### Next steps

[x] Generate Next.js boiler-plate:

   ```bash
   npx create-next-app@latest setlistify-ui --ts --tailwind --app
   cd setlistify-ui && pnpm add next-auth axios swr
   ```

[] Scaffold components & API routes using the contract above.

[] Point proxy to your FastAPI domain.

[] End-to-end test: login → Metallica → preview → playlist link.

