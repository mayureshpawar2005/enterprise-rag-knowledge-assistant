# Enterprise RAG Frontend

Modern React dashboard for the Enterprise RAG Knowledge Assistant.

## Stack

- **React 19** + **TypeScript**
- **Vite** — dev server & build
- **Tailwind CSS v4** — styling
- **shadcn/ui** — component patterns (Button, Card, ScrollArea, etc.)
- **Lucide React** — icons

## Features

- Professional dashboard with health stats
- Drag-and-drop PDF upload (multi-file)
- ChatGPT-style chat interface
- Chat history sidebar (localStorage)
- Source citations panel
- Dark / light mode
- Loading animations
- Responsive layout (mobile sidebar & sources overlays)

## Quick start

**1. Start the FastAPI backend** (port 8000):

```powershell
cd "D:\enterprise rag"
.\run.ps1
```

**2. Install & run the frontend** (port 5173):

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

The Vite dev server proxies `/api/*` → `http://127.0.0.1:8000/*`.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | Backend API base URL |

For production, set `VITE_API_URL` to your deployed API URL before `npm run build`.

## Build

```powershell
npm run build
npm run preview
```

## Project structure

```
frontend/src/
├── components/
│   ├── chat/          # Chat UI
│   ├── layout/        # Header, sidebar
│   ├── sources/       # Citations panel
│   ├── upload/        # Drag-drop upload
│   └── ui/            # shadcn-style primitives
├── hooks/             # useChatStore, useTheme
├── lib/               # API client, utils
└── types/             # TypeScript API types
```
