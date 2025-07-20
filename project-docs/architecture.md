# **Setlistify — System Architecture**

This document describes the architecture of the Setlistify application, which is composed of two main parts: a Python-based AI agent backend and a Next.js frontend.

## 1. AI Agent & Backend Architecture (`src/`)

The backend is a FastAPI server that exposes an AI agent's capabilities. It is responsible for all business logic, including fetching data from external APIs and creating Spotify playlists.

-   **Core Framework:** The backend is built in Python using **FastAPI**, providing a robust and fast way to create API endpoints.

-   **Agent Orchestration:** The core logic is handled by an AI agent built with **`smol-agents`**. This framework manages the interaction between the language model and the available tools.
    -   **LLM:** The agent uses the **`deepseek-ai/DeepSeek-R1`** model hosted on the **Together.ai** platform. Communication is handled via an OpenAI-compatible API endpoint (`src/llm.py`).
    -   **System Prompt:** The agent's behavior is guided by a detailed system prompt (`src/prompts/system.md`) which instructs it on the step-by-step process to achieve its goal (find songs, create a playlist).

-   **Tooling (`src/tools/`)**: The agent has access to a set of Python functions decorated with `@tool`:
    -   **`setlist_tools.py`**: Contains functions (`search_artist`, `get_latest_show`, `extract_setlist`) for interacting with the **Setlist.fm API** to retrieve artist and setlist data.
    -   **`spotify_tools.py`**: Contains the `create_playlist` function, which uses the **`spotipy`** library to handle all interactions with the **Spotify API**.

-   **Authentication & Security:**
    - The backend is stateless regarding users. It expects a valid Spotify access token to be passed in the `Authorization: Bearer <token>` header for any request requiring Spotify access.
    - The `build_agent_for_token` function (`src/agent.py`) is a key security feature. For each user request, it dynamically creates a new agent instance. Inside this function, it defines a wrapper tool (`create_playlist_for_user`) that has the user's access token "baked in." This ensures the sensitive token is never passed as a parameter to the LLM, preventing it from being exposed or logged.

-   **Observability:**
    - The system is instrumented with **OpenTelemetry** to trace agent execution.
    - Traces are exported to **LangFuse**, allowing for detailed logging and debugging of the agent's thought process, tool usage, and final output (`src/agent.py`).

## 2. Frontend Architecture (`setlistify-ui/`)

The frontend is a modern, responsive single-page application that provides the user interface for interacting with the Setlistify service.

-   **Framework:** The UI is built with **Next.js 15** (App Router), **TypeScript**, and styled with **Tailwind CSS**.

-   **Authentication:**
    - **`next-auth`** (v4) is used to handle the entire Spotify OAuth 2.0 authentication flow.
    - It manages the user session, securely stores tokens, and makes the session data (including the crucial `accessToken`) available to the frontend components via the `useSession` hook.
    - The configuration in `setlistify-ui/app/api/auth/[...nextauth]/route.ts` defines the Spotify provider, requested scopes, and callbacks to attach the access token to the session JWT.

-   **UI/Component Structure:**
    - The UI is centered around a multi-step **`<Wizard />`** component (`components/wizard.tsx`) that guides the user through the process.
    - The wizard manages the application state (current step, artist name, song list) using React's `useState` hook.
    - Steps are broken into individual components: `<ChooseBand />`, `<PreviewSetlist />`, and `<CreatePlaylist />`.

-   **Backend Communication (Proxy):**
    - The Next.js frontend does not call the FastAPI backend directly from the browser. Instead, it uses a **rewrite proxy**.
    - The `next.config.ts` file is configured to proxy any requests made to `/api/external/:path*` on the Next.js server to the FastAPI backend at `http://127.0.0.1:8000/api/:path*`.
    - This simplifies CORS configuration and hides the backend's direct address from the client. UI components make calls to local API routes (e.g., `/api/external/agent/setlist`), and Next.js forwards them to the Python server, including the necessary `Authorization` header.