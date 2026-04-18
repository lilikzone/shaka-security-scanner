# Shaka Security Scanner Frontend

Enterprise-grade SOC-style frontend for `Shaka-Security-Scanner`.

## Tech Stack
- Next.js (App Router)
- React + TypeScript
- TailwindCSS
- Zustand state management
- Recharts for security analytics

## Implemented Pages
- `/dashboard` - SOC overview, KPI cards, trends, distribution, recent scans
- `/scans` - scan queue + create scan modal
- `/vulnerabilities` - findings table + drill-down detail panel
- `/insights` - AI insight summary + remediation chat
- `/scans/[scanId]` - timeline, terminal-style logs, issue categories
- `/settings` - API config, AI provider/model settings, notification toggles

## UI Modes
- Pentester Mode: technical-first operator view
- Executive Mode: management-friendly summary mode toggle (foundation ready)

## Security UI Capabilities
- Severity color system and high-risk warning banners
- Risk score emphasis and critical finding spotlight
- Role-based UI scaffolding prepared for multi-tenant RBAC

## Run Locally
```bash
npm install
npm run dev
```

## Production Integration Plan
Replace mock data in `lib/mock-data.ts` with API services:
- `GET /api/v1/scans`
- `POST /api/v1/scans`
- `GET /api/v1/scans/{scan_id}`
- `GET /api/v1/findings`
- `GET /api/v1/insights/{scan_id}`
- `POST /api/v1/insights/chat`

Recommended shape alignment with backend models:
- `ScanSession` -> scan list/detail pages
- `Finding` + `Severity` -> vulnerabilities table and detail panel
- `EnhancedFinding` / AI summary -> insights and executive risk narratives
