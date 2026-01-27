# Monorepo Project

This is a polyglot monorepo containing:
- **Web App**: Next.js (`apps/web`)
- **Mobile App**: React Native / Expo (`apps/mobile`)
- **API**: FastAPI (`apps/api`)
- **Shared Packages**: `packages/ui`, `packages/api-client`, etc.

## Prerequisites
- Node.js (v18+)
- pnpm (`npm install -g pnpm`)
- Python 3.11+ (Conda recommended)

## Setup

### 1. Install Dependencies (Node.js)
```bash
pnpm install
```

### 2. Setup Python Environment
```bash
# Create the environment
conda env create -f apps/api/environment.yml
# Activate
conda activate monorepo-api
```

## Running the Project

### Turbo Mode (All at once)
```bash
pnpm dev
```
This runs `web`, `mobile` (if script exists), and `api` in parallel.

### Individual Apps
- **Web**: `cd apps/web && pnpm dev`
- **API**: `cd apps/api` -> `uvicorn main:app --reload`
- **Mobile**: `cd apps/mobile && npx expo start`

## Architecture
See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.
