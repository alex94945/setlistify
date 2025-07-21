This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

To run this project, you need both the backend and frontend servers running concurrently in separate terminal sessions.

### 1. Start the Backend Server

The backend server provides the core API for the application.

1.  Open a terminal and navigate to the **root directory** of the project (`/setlistify`).
2.  Activate the conda environment:
    ```bash
    conda activate setlistify
    ```
3.  Start the Uvicorn server:
    ```bash
    uvicorn src.server:app --reload
    ```
The backend will now be running at `http://127.0.0.1:8000`.

### 2. Start the Frontend Server

The frontend is a Next.js application.

1.  Open a **new, separate terminal** and navigate to the UI directory (`/setlistify/setlistify-ui`).
2.  Run the development server using your preferred package manager:
    ```bash
    npm run dev
    ```
    **Note:** `npm run dev`, `pnpm dev`, and `yarn dev` all execute the same command. **Do not run more than one at the same time**, as this will cause port conflicts.

Open [http://http://127.0.0.1:3000/](http://http://127.0.0.1:3000/) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
