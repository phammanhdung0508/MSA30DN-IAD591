# Production Monorepo Architecture Design

## Overview
This architecture implements a hybrid monorepo supporting TypeScript (Frontend) and Python (Backend). It utilizes **pnpm** for package management (Node.js), **Conda** for Python environment management, and **Turborepo** for build orchestration.

## Directory Structure
```
/
├── apps/
│   ├── api/            # FastAPI backend (Python 3.11+)
│   ├── mobile/         # React Native (Expo) app
│   └── web/            # Web application (Next.js or Vite)
├── packages/
│   ├── ui/             # Shared React UI components
│   ├── api-client/     # Auto-generated TypeScript client from OpenAPI
│   ├── tsconfig/       # Shared TypeScript configurations
│   └── eslint-config/  # Shared Linting configurations
├── tooling/
│   └── scripts/        # Build/Generate scripts (e.g., OpenAPI generation)
├── turbo.json          # Pipeline configuration
├── pnpm-workspace.yaml # Workspace definitions
└── package.json        # Root dependencies and scripts
```

## Key Architectural Decisions

### 1. Build System & Workflow
- **Turborepo** controls the lifecycle (build, test, lint, dev).
- **pnpm workspaces** manages Node.js dependencies and linking.
- **Conda** manages Python environment and dependencies within `apps/api` (using `environment.yml`).

### 2. Type Safety & API Contract
- **Source of Truth**: The FastAPI backend (`apps/api`).
- **Generation Flow**:
    1. `packages/api-client` runs a script to fetch/read this schema.
    2. `packages/api-client` uses a generator (e.g., `openapi-typescript-codegen`) to produce typed SDKs.
    3. `apps/web` and `apps/mobile` consume `packages/api-client` directly.

### 3. Frontend Architecture
- **Shared UI**: `packages/ui` exports a Component Library (likely using Tamagui, NativeBase, or React Native Paper + Web support for unified code, or just separated logic if preferring distinct UIs).
- **Mobile**: Uses Expo for rapid development and OTA updates.
- **Web**: Uses Next.js/Vite for performance.

### 4. Backend Architecture
- **Framework**: FastAPI for async performance and auto-docs.
- **Validation**: Pydantic models (shared easily via OpenAPI).
- **DevEx**: Live reload via `uvicorn`.

## CI/CD Pipeline Strategy
- **Caching**: Turbo Remote Caching to avoid rebuilding unchanged packages.
- **Pruning**: `turbo prune --scope=<target>` to create Docker slices for deployment.
- **Deployment**:
    - **API**: Dockerized Python container (built from pruned context).
    - **Web**: Vercel or Dockerized node container.
    - **Mobile**: EAS (Expo Application Services) Build.
