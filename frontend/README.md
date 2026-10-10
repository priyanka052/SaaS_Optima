# SaaSOptima frontend starter

This is a lightweight Vite frontend for the backend APIs found in the uploaded branch ZIPs. It includes Overview, Tools, Pricing, Compare, Feature Overlap, and Negotiation screens, with shared API requests and loading, error, and empty states.

## Run it

1. Start the FastAPI backend from the branch that includes the required API routers. The negotiation branch ZIP currently includes tools, pricing, overlap, compare, and negotiation routes.
2. From this folder, run `npm install` once, then `npm run dev`.
3. Open the local Vite URL shown in the terminal. The Vite development server forwards `/api` requests to `http://127.0.0.1:8000`.

The backend must be running on port 8000. To use another address, update `vite.config.js`.

## API routes used

- `GET /api/health`
- `GET /api/tools`
- `GET /api/pricing`
- `GET /api/overlap?threshold=0`
- `GET /api/compare?tool_a=...&tool_b=...`
- `POST /api/negotiation`

The uploaded branches do not expose a standalone recommendations endpoint. The comparison and overlap results show the backend's available lower-price suggestions instead.
